# Copyright 2023, themeontology.org
# Tests:
import gzip
import json
import os.path
import pickle
import re
import shutil
import urllib.request
from collections import defaultdict

import pymysql
from django.core.management.base import BaseCommand
from django.db import transaction
from unidecode import unidecode

import lib.files
import lib.git
import lib.graph
import themeontology
import totolo.deployment
from ontologyexplorer.models import Story, Theme, StoryTheme, Statistic

URL_GIT_INFO = "https://api.github.com/repos/theme-ontology/theming/branches/master"
RE_WORD = "[^\W_]+"


def ontology_to_django(to):
    """
    Read from ontology. Store in Django DB. Return some stats.
    """
    stcount = defaultdict(int)
    wordcount = defaultdict(int)
    collections = defaultdict(set)
    themed_stories = 0
    defined_themes = 0
    motivationwordcounts = []
    theme_graph = lib.graph.KWGraph()

    for story in to.stories():
        for child in story.get("Component Stories"):
            collections[child].add(story.sid)
    for theme in to.themes():
        for parent in theme.get("Parents"):
            theme_graph.makeEdge(parent, theme.name)
    levels = theme_graph.top_sort()
    print("Theme roots:", theme_graph.findRoots())

    with transaction.atomic():
        Story.objects.all().delete()
        for story in to.stories():
            all_collections = set(story.get("Collections"))
            all_collections.update(collections[story.sid])
            Story(
                sid=story.sid,
                title=story.title,
                date=story.date,
                parents=', '.join(sorted(all_collections)),
                children=', '.join(story.get("Component Stories")),
                description=story.html_description(),
                description_short=story.html_short_description(),
                ratings=story.get("Ratings"),
            ).save()
    with transaction.atomic():
        Theme.objects.all().delete()
        for theme in to.themes():
            defined_themes += 1
            Theme(
                name=theme.name,
                parents=', '.join(theme.get("Parents")),
                children=', '.join(sorted(theme_graph.children_of(theme.name))),
                level=levels[theme.name],
                description=theme.html_description(),
                description_short=theme.html_short_description(),
            ).save()
    with transaction.atomic():
        StoryTheme.objects.all().delete()
        for story in to.stories():
            is_themed = False
            sid = story.sid
            for weight in ["choice", "major", "minor", "not"]:
                field = "{} Themes".format(weight.capitalize())
                for kw in story.get(field):
                    is_themed = True
                    numwords = len(re.findall(RE_WORD, kw.motivation))
                    if numwords:
                        stcount[weight] += 1
                        wordcount["motivation"] += numwords
                        motivationwordcounts.append(numwords)
                    StoryTheme(
                        sid=sid,
                        theme=kw.keyword,
                        weight=weight,
                        motivation=kw.motivation,
                        capacity=kw.capacity,
                        notes=kw.notes,
                    ).save()
            if is_themed:
                themed_stories += 1

    motivationwordcounts.sort()
    return {
        "num_stories": themed_stories,
        "num_themes": defined_themes,
        "num_storythemes": dict(stcount),
        "num_words": wordcount,
        "motivation_wordcount_10pct": motivationwordcounts[len(motivationwordcounts)*9//10],
    }


def django_to_sphinx(wordcount):
    """
    Read from Django DB. Index to Sphinx. Return dictionaries of words.
    """
    corpus = defaultdict(int)
    diacritics = defaultdict(set)
    conn = pymysql.connect(
        host=totolo.deployment.SPHINX.HOST,
        port=totolo.deployment.SPHINX.PORT,
        user='', passwd='', charset='utf8', db='',
    )
    cur = conn.cursor()
    cur.execute("TRUNCATE RTINDEX totolo_stories")
    conn.commit()
    for story in Story.objects.all():
        all_word_lists = [
            re.findall(RE_WORD, story.title),
            re.findall(RE_WORD, story.description),
        ]
        for word_list in all_word_lists:
            wordcount["story_description"] += len(word_list)
            for word in word_list:
                corpus[word.lower()] += 1
        qry = "INSERT INTO totolo_stories (id, title, description) VALUES (%s, %s, %s)"
        cur.execute(qry, (story.idx, story.title, story.description))
    conn.commit()
    cur.execute("TRUNCATE RTINDEX totolo_themes")
    conn.commit()
    for theme in Theme.objects.all():
        all_word_lists = [
            re.findall(RE_WORD, theme.name),
            re.findall(RE_WORD, theme.description),
        ]
        for word_list in all_word_lists:
            wordcount["theme_description"] += len(word_list)
            for word in word_list:
                lword = word.lower()
                asciiword = unidecode(lword)
                corpus[lword] += 1
                if asciiword != lword:
                    diacritics[asciiword].add(lword)
        qry = "INSERT INTO totolo_themes (id, name, description) VALUES (%s, %s, %s)"
        cur.execute(qry, (theme.idx, theme.name, theme.description))
    conn.commit()
    cur.close()
    conn.close()
    return corpus, diacritics


class Command(BaseCommand):
    help = 'Download head version of git repo and index it.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # prepare, get repository and read data
        base = os.path.join(totolo.deployment.TEMP_PATH, "gitmonitor")
        repo = os.path.join(base, "theming")
        shutil.rmtree(base, True)
        lib.files.mkdirs(repo)
        lib.git.download_headversion("https://github.com/theme-ontology", "theming", repo)
        to = themeontology.read(os.path.join(repo, "notes"), imply_collection=True)
        to.print_warnings()

        # get some info about the state of our repository
        with urllib.request.urlopen(URL_GIT_INFO) as url:
            head_version_info = json.load(url)
            timestamp = head_version_info["commit"]["commit"]["committer"]["date"]
            print("downloaded head version as of: {}".format(timestamp))

        # do the heavy lifting
        stats = ontology_to_django(to)
        corpus, diacritics = django_to_sphinx(stats["num_words"])

        # Store some extra information on disk and in Django DB
        with gzip.open("/code/tmp/totolo_corpus.pickle.gz", "w+") as fh:
            pickle.dump(dict(corpus), fh)
        with gzip.open("/code/tmp/totolo_diacritics.pickle.gz", "w+") as fh:
            pickle.dump(dict(diacritics), fh)
        with gzip.open("/code/tmp/totolo_statistics.pickle.gz", "w+") as fh:
            pickle.dump(dict(stats), fh)
        Statistic.objects.update_or_create(
            name="general_stats",
            timestamp=timestamp,
            defaults={
                "data": gzip.compress(pickle.dumps(stats)),
            },
        )

        # clean up and exit
        shutil.rmtree(base, True)
        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return


