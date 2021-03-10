import webdb
from lib.wikiparsers import find_episodes_st1
import sys


def main():
    fn = sys.argv[-1]

    urls = [
        "https://en.wikipedia.org/wiki/Disenchantment_(TV_series)#Part_3_(2021)",
    ]
    stories = {}

    for idx, url in enumerate(urls):
        # cols:
        # titlefield, directorfield, authorfield, datefield
        for story in find_episodes_st1(
            url, 1, "disenchantment2018e", cols=(1, 2, 3, 4), isterse=False, tableclass="wikiepisodetable",
        ):
            stories[story.name] = story

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
