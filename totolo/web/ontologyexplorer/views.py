from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from .models import Theme, Story, Statistic
from .serializers import StorySerializer, ThemeSerializer, StoryDTSerializer, ThemeDTSerializer
import totolo.search
import gzip
import pickle
import traceback


def index(request):
    ERR = "&lt;calculating...&gt;"
    try:
        statsobj = Statistic.objects.filter(name="general_stats").order_by("-timestamp")[0]
        stats = pickle.loads(gzip.decompress(statsobj.data))
    except Exception:
        print(traceback.format_exc())
        stats = {}

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


def story(request, sid):
    storyobj = Story.objects.get(sid=sid)
    template = loader.get_template("ontologyexplorer/story.html")
    context = {'storyobj': storyobj}
    return HttpResponse(template.render(context, request))


def theme(request, name):
    themeobj = Theme.objects.get(name=name)
    template = loader.get_template("ontologyexplorer/theme.html")
    context = {'themeobj': themeobj}
    return HttpResponse(template.render(context, request))


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def list(self, request):
        if request.GET.get('format', None) == "datatables":
            self.serializer_class = StoryDTSerializer
        query = request.GET.get('query', None)
        if query:
            idx2weight = {t.idx: w for (t, w) in totolo.search.stories(query)}
            query_set = Story.objects.filter(idx__in=idx2weight.keys())
            serial = self.serializer_class(query_set, many=True, weight_index=idx2weight)
            return Response(serial.data, status=status.HTTP_200_OK)
        else:
            return super().list(request)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def list(self, request):
        if request.GET.get('format', None) == "datatables":
            self.serializer_class = ThemeDTSerializer
        query = request.GET.get('query', None)
        if query:
            idx2weight = {t.idx: w for (t, w) in totolo.search.themes(query)}
            query_set = Theme.objects.filter(idx__in=idx2weight.keys())
            serial = self.serializer_class(query_set, many=True, weight_index=idx2weight)
            return Response(serial.data, status=status.HTTP_200_OK)
        else:
            return super().list(request)

