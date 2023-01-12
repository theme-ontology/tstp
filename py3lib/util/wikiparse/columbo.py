import webdb
from lib.wikiparsers import find_episodes_st1
import sys


def main():
    fn = sys.argv[-1]

    urls = [
        "https://en.wikipedia.org/wiki/Columbo_(season_1)",
        "https://en.wikipedia.org/wiki/Columbo_(season_2)",
        "https://en.wikipedia.org/wiki/Columbo_(season_3)",
        "https://en.wikipedia.org/wiki/Columbo_(season_4)",
        "https://en.wikipedia.org/wiki/Columbo_(season_5)",
        "https://en.wikipedia.org/wiki/Columbo_(season_6)",
        "https://en.wikipedia.org/wiki/Columbo_(season_7)",
        "https://en.wikipedia.org/wiki/Columbo_(season_8)",
        "https://en.wikipedia.org/wiki/Columbo_(season_9)",
        "https://en.wikipedia.org/wiki/Columbo_(season_10)",
    ]
    stories = {}

    url = "https://en.wikipedia.org/wiki/List_of_Columbo_episodes"
    for story in find_episodes_st1(
            url, 0, "columbo1971e", cols=(0, 1, 2, 5), isterse=False, tableclass="wikitable", table_limit=1, singleseason=True
    ):
        stories[story.name] = story

    for idx, url in enumerate(urls):
        # cols:
        # titlefield, directorfield, authorfield, datefield
        for story in find_episodes_st1(
            url, idx+1, "columbo1971e", cols=(1, 2, 3, 6), isterse=False, tableclass="wikitable", table_limit=1
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
