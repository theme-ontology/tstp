from lib.wikiparsers2 import find_episodes_st1
import sys
import totolo


def main():
    to = totolo.empty()
    fn = sys.argv[-1]
    to.entries[fn] = []

    url = "https://en.wikipedia.org/wiki/List_of_Love,_Death_%26_Robots_episodes"
    for story in find_episodes_st1(
            url, 1, "ldr2019e", cols=(1, 2, 4, 6), isterse=False, tableclass="wikiepisodetable",
            singleseason=False
    ):
        print(story.name, story.title, f"({story.date})")
        to.entries[fn].append(story)
        story.source_location = fn

    to.write_clean()
