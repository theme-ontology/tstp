import webdb
from lib.wikiparsers import find_table_story_entries
import sys


def main():
    fn = sys.argv[-1]

    urls = [
        "https://en.wikipedia.org/wiki/Alfred_Hitchcock_filmography",
    ]
    stories = {}

    for idx, url in enumerate(urls):
        # cols:
        # titlefield, directorfield, authorfield, datefield
        for story in find_table_story_entries(
            url, prefix="movie: ", cols=(1, -1, -1, 0), tableclass="wikitable", table_idxs=[0]
        ):
            stories[(story.date, story.name)] = story

    objs = [stories[sid] for sid in sorted(stories)]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True, presorted=True,
                                                 skip_fields=('collections',), add_fields=("Ratings",))

    if fn.endswith(".txt"):
        txt = txt.encode("utf-8")
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
