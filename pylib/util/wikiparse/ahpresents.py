import webdb
from lib.wikiparsers import find_episodes_st1
import sys


def main():
    fn = sys.argv[-1]

    urls = [
        "https://en.wikipedia.org/wiki/List_of_Alfred_Hitchcock_Presents_episodes",
    ]
    stories = {}

    for idx, url in enumerate(urls):
        # cols:
        # titlefield, directorfield, authorfield, datefield
        for story in find_episodes_st1(
            url, 1, "ahp", cols=(1, 2, 3, 5), isterse=False, tableclass="wikitable", table_offset=1
        ):
            stories[story.name] = story

    objs = [stories[sid] for sid in sorted(stories)]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True, skip_fields=('collections',),
                                                 add_fields=("Ratings",))
    txt = txt.encode("utf-8")

    if fn.endswith(".txt"):
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
