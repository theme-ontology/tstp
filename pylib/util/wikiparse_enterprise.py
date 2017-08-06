import urllib2
from bs4 import BeautifulSoup
import webdb
from wikiparsers import find_episodes_st1


def main():
    urls = [
        "https://en.wikipedia.org/wiki/Star_Trek:_Enterprise_(season_1)",
        "https://en.wikipedia.org/wiki/Star_Trek:_Enterprise_(season_2)",
        "https://en.wikipedia.org/wiki/Star_Trek:_Enterprise_(season_3)",
        "https://en.wikipedia.org/wiki/Star_Trek:_Enterprise_(season_4)",
    ]
    stories = {}

    for idx, url in enumerate(urls):
        for story in find_episodes_st1(
            url, idx + 1, "ent", tableclass = "wikiepisodetable", cols = (1, 2, 3, 4)
        ):
            stories[story.name] = story

    objs = [ stories[sid] for sid in sorted(stories) ]
    txt = webdb.get_defenitions_text_for_objects(objs)

    print txt.encode("utf-8")
