import urllib2
from bs4 import BeautifulSoup
import webdb
from wikiparsers import find_episodes_st1


def main():
    url = "https://en.wikipedia.org/wiki/List_of_Babylon_5_episodes"
    stories = {}

    for story in find_episodes_st1(url, -1, "bbf", cols = (1, 2, 3, 4)):
        stories[story.name] = story

    objs = [ stories[sid] for sid in sorted(stories) ]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers = True)

    print txt.encode("utf-8")

