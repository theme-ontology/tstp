from flask import Flask
from flask_graphql import GraphQLView
from graphene import String, Int
import graphene
import webobject
import re
from credentials import GIT_THEMING_PATH
import lib.files
import log
import os.path
import lib.dataparse


import logging
logging.getLogger("graphql.execution.utils")

CACHED_STORIES = {}


def get_raw_stories():
    if not CACHED_STORIES:
        path = os.path.join(GIT_THEMING_PATH, "notes")
        cs = CACHED_STORIES
        for path in lib.files.walk(path, ".*\.(st|th)\.txt$", 0):
            log.info("READING: %s", path)
            if path.endswith(".st.txt"):
                for obj in lib.dataparse.read_stories_from_txt(path, addextras=True):
                    cs[obj.name] = obj

    return CACHED_STORIES


class TSTPBaseType(graphene.ObjectType):
    @classmethod
    def from_data(cls, obj):
        kwargs = {}
        for attr in type(obj).fields:
            kwargs[attr] = getattr(obj, attr)
        obj = cls(**kwargs)
        return obj


StoryTypeBase = type('StoryTypeBase', (TSTPBaseType,), {k: String() for k in webobject.Story.fields})
ThemeTypeBase = type('ThemeTypeBase', (TSTPBaseType,), {k: String() for k in webobject.Theme.fields})


class StoryType(StoryTypeBase):
    themes = graphene.List(lambda: ThemeType)
    ratings = graphene.List(Int, by=graphene.String())
    rating = graphene.Float(by=graphene.String())

    def resolve_themes(self, info):
        links = webobject.StoryTheme.load(name1s=[self.name])
        linkids = [ l.name2 for l in links ]
        targets = webobject.Theme.load(names=linkids)
        return [ ThemeType.from_data(obj) for obj in targets ]

    def resolve_ratings(self, info, by=None):
        lu = get_raw_stories()
        obj = lu.get(self.name, None)
        ratingstxt = []
        ratingsint = []
        if obj:
            ratingstxt = getattr(obj, 'ratings', [])
        filter = [x.strip().lower() for x in (by or '').split(",")]
        for rt in ratingstxt:
            match = re.search(r"(\d+).*<([^\>]+)>", rt)
            if match:
                if not by or match.group(2).lower() in filter:
                    ratingsint.append(int(match.group(1)))

        return ratingsint

    def resolve_rating(self, info, by=None):
        ratings = self.resolve_ratings(info, by=by)
        if ratings:
            return sum(ratings) / float(len(ratings))
        return 3.5


class ThemeType(ThemeTypeBase):
    stories = graphene.List(lambda: StoryType)

    def resolve_stories(self, info):
        links = webobject.StoryTheme.load(name2s=[self.name])
        linkids = [ l.name1 for l in links ]
        targets = webobject.Story.load(names=linkids)
        return [ StoryType.from_data(obj) for obj in targets ]


class TSTPQuery(graphene.ObjectType):
    stories = graphene.List(StoryType, sidlike=graphene.String())

    def resolve_stories(self, info, sidlike=None, **kwarg):
        targets = []
        for obj in  webobject.Story.load():
            if sidlike:
                if not re.match(sidlike, obj.name):
                    continue
            targets.append(obj)

        sids = [ o.name for o in targets ]
        return [
            StoryType.from_data(obj) for obj in targets
        ]


def create_app():
    schema = graphene.Schema(query=TSTPQuery)
    app = Flask(__name__)
    app.debug = True
    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True, context={'session': None}))

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        pass

    return app


# can't use pyrun command because of Flask's messed up "reloader"
if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8182, debug=False)




