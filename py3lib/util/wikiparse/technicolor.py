import webdb
from lib.wikiparsers import fetch_table_list
import sys


def main():
    fn = sys.argv[-1]

    urls = [
        "https://en.wikipedia.org/wiki/List_of_three-strip_Technicolor_films",
    ]
    stories = {}

    for idx, url in enumerate(urls):
        # cols:
        # titlefield, directorfield, authorfield, datefield
        for story in fetch_table_list(
            url, cols=(0, 1, 5, 2)
        ):
            stories[story.name] = story
            #if len(stories) > 5: break

    objs = [ stories[sid] for sid in sorted(stories) ]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True,
                                                 skip_fields=('collections',), add_fields=("Ratings",))

    if fn.endswith(".txt"):
        txt = txt.encode("utf-8")
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
