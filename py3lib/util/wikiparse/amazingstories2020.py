from lib.wikiparsers2 import find_episodes_st1
import sys
import totolo


def main():
    to = totolo.empty()
    fn = sys.argv[-1]
    to.entries[fn] = []

    url = "https://en.wikipedia.org/wiki/Amazing_Stories_(2020_TV_series)"
    for story in find_episodes_st1(
            url, 1, "as2020e", cols=(0, 1, 2, 3), isterse=False, tableclass="wikiepisodetable",
            singleseason=True
    ):
        print(story.name)
        to.entries[fn].append(story)
        story.source_location = fn

    to.write_clean()
