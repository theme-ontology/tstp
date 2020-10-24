import webdb
from lib.wikiparsers import find_episodes_st1


def main():
    url_ds9_main = "https://en.wikipedia.org/wiki/List_of_Star_Trek:_Deep_Space_Nine_episodes"
    stories = {}

    for story in find_episodes_st1(url_ds9_main, 0, "ds9", tableclass = "wikitable"):
        stories[story.name] = story

    objs = [ stories[sid] for sid in sorted(stories) ]
    txt = webdb.get_defenitions_text_for_objects(objs)

    print(txt.encode("utf-8"))


