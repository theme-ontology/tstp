from lib.wikiparsers2 import find_episodes_st1
import sys
import totolo


def main():
    to = totolo.empty()
    fn = sys.argv[-1]
    to.entries[fn] = []

    url = "https://en.wikipedia.org/wiki/Amazing_Stories_(1985_TV_series)"
    for story in find_episodes_st1(
            url, 1, "as1985e", cols=(1, 2, 3, 4), isterse=False, tableclass="wikiepisodetable",
    ):
        to.entries[fn].append(story)
        story.source_location = fn

    to.write_clean()
