import urllib2
from bs4 import BeautifulSoup
import webdb
from wikiparsers import find_episodes_st1


def main():
    url_voy_main = "https://en.wikipedia.org/wiki/List_of_Star_Trek:_Voyager_episodes"
    url_voy_s4 = "https://en.wikipedia.org/wiki/Star_Trek:_Voyager_(season_4)"
    stories = {}

    for story in find_episodes_st1(url_voy_main, 0, "voy"):
        stories[story.name] = story
    for story in find_episodes_st1(url_voy_s4, 4, "voy", tableclass = "wikiepisodetable"):
        stories[story.name] = story

    objs = [ stories[sid] for sid in sorted(stories) ]
    txt = webdb.get_defenitions_text_for_objects(objs)

    print txt.encode("utf-8")
