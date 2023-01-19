# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
from ontologyexplorer.models import Story, Theme, StoryTheme
import lib.git
import credentials
import os.path
import lib.files
import shutil
import themeontology
from django.db import transaction
from collections import defaultdict
import pymysql
import re
import gzip
import pickle


RE_WORD = "[^\W_]+"


class Command(BaseCommand):
    help = 'Download head version of git repo and index it.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # prepare, get repository and read data
        base = os.path.join(credentials.TEMP_PATH, "gitmonitor")
        repo = os.path.join(base, "theming")
        shutil.rmtree(base, True)
        lib.files.mkdirs(repo)
        lib.git.download_headversion("https://github.com/theme-ontology", "theming", repo)
        to = themeontology.read(os.path.join(repo, "notes"))
        children = defaultdict(set)

        # read data from repository and save in db
        for theme in to.themes():
            for parent in theme.get("Parents"):
                children[parent].add(theme.name)
        with transaction.atomic():
            Story.objects.all().delete()
            for story in to.stories():
                Story(
                    sid=story.sid,
                    title=story.title,
                    date=story.date,
                    parents=story.get("Collections"),
                    children=story.get("Component Stories"),
                    description=story.html_description(),
                    ratings=story.get("Ratings"),
                ).save()
        with transaction.atomic():
            Theme.objects.all().delete()
            for theme in to.themes():
                Theme(
                    name=theme.name,
                    parents=', '.join(theme.get("Parents")),
                    children=', '.join(sorted(children[theme.name])),
                    description=theme.html_description(),
                ).save()
        with transaction.atomic():
            StoryTheme.objects.all().delete()
            for story in to.stories():
                sid = story.sid
                for weight in ["choice", "major", "minor", "not"]:
                    field = "{} Themes".format(weight.capitalize())
                    for kw in story.get(field):
                        StoryTheme(
                            sid=sid,
                            theme=kw.keyword,
                            weight=weight,
                            motivation=kw.motivation,
                            capacity=kw.capacity,
                            notes=kw.notes,
                        ).save()

        # index data in Sphinx
        corpus = defaultdict(int)
        conn = pymysql.connect(
            host=credentials.SERVER_SPHINX,
            port=credentials.PORT_SPHINX,
            user='', passwd='', charset='utf8', db='',
        )
        cur = conn.cursor()
        cur.execute("TRUNCATE RTINDEX totolo_stories")
        conn.commit()
        for story in Story.objects.all():
            for word in re.findall(RE_WORD, story.title):
                corpus[word.lower()] += 1
            for word in re.findall(RE_WORD, story.description):
                corpus[word.lower()] += 1
            qry = "INSERT INTO totolo_stories (id, title, description) VALUES (%s, %s, %s)"
            cur.execute(qry, (story.idx, story.title, story.description))
        conn.commit()
        cur.execute("TRUNCATE RTINDEX totolo_themes")
        conn.commit()
        for theme in Theme.objects.all():
            for word in re.findall(RE_WORD, theme.name):
                corpus[word.lower()] += 1
            for word in re.findall(RE_WORD, theme.description):
                corpus[word.lower()] += 1
            qry = "INSERT INTO totolo_themes (id, name, description) VALUES (%s, %s, %s)"
            cur.execute(qry, (theme.idx, theme.name, theme.description))
        conn.commit()
        cur.close()
        conn.close()
        with gzip.open("/code/tmp/totolo_corpus.pickle.gz", "w+") as fh:
            pickle.dump(corpus, fh)

        # clean up and exit
        shutil.rmtree(base, True)
        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return
