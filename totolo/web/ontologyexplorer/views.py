from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from .models import Story, Theme, StoryTheme, Statistic, S3Link
import ontologyexplorer.serializers as s
import totolo.search
import gzip
import pickle
import traceback
from collections import defaultdict
import os.path
import time


def index(request):
    ERR = "&lt;calculating...&gt;"
    try:
        statsobj = Statistic.objects.filter(name="general_stats").order_by("-timestamp")[0]
        stats = pickle.loads(gzip.decompress(statsobj.data))
    except Exception:
        stats = {}
        context = {
            "num_stories": "(calculating...)",
            "num_themes": "(calculating...)",
            "num_motivations": "(calculating...)",
            "num_motivations_choice": "(calculating...)",
            "num_motivations_major": "(calculating...)",
            "num_motivations_minor": "(calculating...)",
            "num_words_story_description": "(calculating...)",
            "num_words_theme_description": "(calculating...)",
            "avg_motivations_per_story": "(calculating...)",
            "avg_words_story_description": "(calculating...)",
            "avg_words_theme_description": "(calculating...)",
            "avg_words_motivation": "(calculating...)",
            "motivation_wordcount_10pct": "(calculating...)",
        }
    else:
        num_motivations = sum(stats.get("num_storythemes", ERR).values())
        nst_stats = stats.get("num_storythemes", {})
        nw_stats = stats.get("num_words", {})
        num_words_story_description = nw_stats.get("story_description", ERR)
        num_words_theme_description = nw_stats.get("theme_description", ERR)
        context = {
            "num_stories": stats.get("num_stories", ERR),
            "num_themes": stats.get("num_themes", ERR),
            "num_motivations": num_motivations,
            "num_motivations_choice": nst_stats.get("choice", ERR),
            "num_motivations_major": nst_stats.get("major", ERR),
            "num_motivations_minor": nst_stats.get("minor", ERR),
            "num_words_story_description": num_words_story_description,
            "num_words_theme_description": num_words_theme_description,
        }
        try:
            context.update({
                "avg_motivations_per_story": num_motivations // stats["num_stories"],
                "avg_words_story_description": num_words_story_description // stats["num_stories"],
                "avg_words_theme_description": num_words_theme_description // stats["num_themes"],
                "avg_words_motivation": nw_stats["motivation"] // num_motivations,
                "motivation_wordcount_10pct": stats.get("motivation_wordcount_10pct", ERR),
            })
        except Exception:
            print(traceback.format_exc())
    template = loader.get_template("ontologyexplorer/index.html")
    return HttpResponse(template.render(context, request))


def stories(request):
    template = loader.get_template("ontologyexplorer/stories.html")
    return HttpResponse(template.render({}, request))


def themes(request):
    template = loader.get_template("ontologyexplorer/themes.html")
    return HttpResponse(template.render({}, request))


def logs(request, name=None):
    choices = [
        "cache_lto",
        "indexgit",
        "query",
    ]
    context = {
        "choices": choices,
        "logname": "",
        "logcontent": "",
        "logmodified": "",
    }
    filename = "/var/log/{}.log".format(name)
    if name in choices:
        context["logname"] = name
        if os.path.isfile(filename):
            dtmod = os.path.getmtime(filename)
            with open(filename, "r") as fh:
                context["logcontent"] = fh.read()
            context["logmodified"] = time.ctime(dtmod)
    template = loader.get_template("ontologyexplorer/logs.html")
    return HttpResponse(template.render(context, request))


def data(request):
    bucket = request.GET.get('bucket', None)
    bybucket = defaultdict(list)
    if bucket:
        links = S3Link.objects.filter(bucket=bucket).order_by("bucket", "name")
    else:
        links = S3Link.objects.all().order_by("bucket", "name")
    for link in links:
        bybucket[link.bucket].append(link)
    links_in_buckets = [
        (
            bucket,
            bybucket[bucket],
        )
        for bucket in sorted(bybucket.keys())
    ]
    context = {
        "links_in_buckets": links_in_buckets,
    }
    template = loader.get_template("ontologyexplorer/data.html")
    return HttpResponse(template.render(context, request))


def story(request, sid):
    try:
        storyobj = Story.objects.get(sid=sid)
    except Story.DoesNotExist:
        return HttpResponseBadRequest('No such story in database: {}.'.format(sid))
    template = loader.get_template("ontologyexplorer/story.html")
    context = {'storyobj': storyobj}
    return HttpResponse(template.render(context, request))


def theme(request, name):
    try:
        themeobj = Theme.objects.get(name=name)
    except Theme.DoesNotExist:
        return HttpResponseBadRequest('No such theme in database: {}.'.format(name))
    template = loader.get_template("ontologyexplorer/theme.html")
    context = {'themeobj': themeobj}
    return HttpResponse(template.render(context, request))


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().order_by("date")[:100]
    serializer_class = s.StorySerializer

    def list(self, request):
        if request.GET.get('format', None) == "datatables":
            self.serializer_class = s.StorySearchDTSerializer

        query = request.GET.get('query', None)
        relativesof = request.GET.get('relativesof', None)

        if query == "" and relativesof is None:
            relativesof = "Collection: William Shakespeare Plays"

        if query:  ## text search
            idx2weight = {t.idx: w for (t, w) in totolo.search.stories(query)}
            query_set = Story.objects.filter(idx__in=idx2weight.keys())
            serial = self.serializer_class(query_set, many=True, weight_index=idx2weight)
            return Response(serial.data, status=status.HTTP_200_OK)

        idx2relation = {}
        if relativesof:  ## get relatives of a story
            try:
                storyobj = Story.objects.get(sid=relativesof)
            except Exception:
                print(traceback.format_exc())
                return HttpResponseBadRequest('Oops, something went wrong with that request.')
            parents = storyobj.parents.split(", ")
            parentset = set(parents)
            children = storyobj.children.split(", ")
            query_set = Story.objects.filter(sid__in=sorted(set(parents+children)))
            for obj in query_set:
                idx2relation[obj.idx] = 'parent' if obj.sid in parentset else 'child'
            serial = self.serializer_class(query_set, relation_index=idx2relation, many=True)
            return Response(serial.data, status=status.HTTP_200_OK)

        else:
            return super().list(request)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all().order_by("level", "parents", "name")[:20]
    serializer_class = s.ThemeSerializer

    def list(self, request):
        if request.GET.get('format', None) == "datatables":
            self.serializer_class = s.ThemeSearchDTSerializer

        query = request.GET.get('query', None)
        parentsof = request.GET.get('parentsof', None)
        childrenof = request.GET.get('childrenof', None)
        relativesof = request.GET.get('relativesof', None)

        if query:  ## text search
            idx2weight = {t.idx: w for (t, w) in totolo.search.themes(query)}
            query_set = Theme.objects.filter(idx__in=idx2weight.keys())
            serial = self.serializer_class(query_set, many=True, weight_index=idx2weight)
            return Response(serial.data, status=status.HTTP_200_OK)

        elif parentsof or childrenof or relativesof:  ## get relatives of a theme
            try:
                themeobj = Theme.objects.get(name=parentsof or childrenof or relativesof)
            except Exception:
                print(traceback.format_exc())
                return HttpResponseBadRequest('Oops, something went wrong with that request.')
            idx2relation = {}
            if parentsof:
                parents = themeobj.parents.split(", ")
                parentset = set(parents)
                query_set = Theme.objects.filter(name__in=parents)
            elif childrenof:
                children = themeobj.children.split(", ")
                parentset = set()
                query_set = Theme.objects.filter(name__in=children)
            else:
                parents = themeobj.parents.split(", ")
                parentset = set(parents)
                children = themeobj.children.split(", ")
                query_set = Theme.objects.filter(name__in=sorted(set(parents+children)))
            for obj in query_set:
                idx2relation[obj.idx] = 'parent' if obj.name in parentset else 'child'
            serial = self.serializer_class(query_set, relation_index=idx2relation, many=True)
            return Response(serial.data, status=status.HTTP_200_OK)

        else:
            return super().list(request)


class StoryThemeViewSet(viewsets.ModelViewSet):
    queryset = StoryTheme.objects.all()
    serializer_class = s.StoryThemeSerializer

    def list(self, request):
        featuringtheme = request.GET.get('featuringtheme', None)
        featuringstory = request.GET.get('featuringstory', None)

        if featuringtheme or featuringstory:
            if featuringtheme:
                query_set = StoryTheme.objects.all().filter(theme=featuringtheme)
            elif featuringstory:
                query_set = StoryTheme.objects.all().filter(sid=featuringstory)
            serial = self.serializer_class(query_set, many=True)
            return Response(serial.data, status=status.HTTP_200_OK)

        else:
            return super().list(request)



