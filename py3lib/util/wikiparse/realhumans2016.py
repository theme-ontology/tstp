from lib.wikiparsers2 import find_episodes_st1
import sys
import totolo


def main():
    to = totolo.empty()
    fn = sys.argv[-1]
    to.entries[fn] = []

    url = "https://en.wikipedia.org/wiki/Real_Humans"
    for story in find_episodes_st1(
            url, 1, "rh2012e", cols=(1, 2, 3, 4), isterse=False, tableclass="wikiepisodetable",
            singleseason=False
    ):
        print(story.name, story.title, f"({story.date})")
        to.entries[fn].append(story)
        story.source_location = fn

    if fn.endswith(".txt"):
        to.write_clean()
        print(f"wrote '{fn}'")
    else:
        print(f"not writing filename '{fn}' because it doesn't end with .txt")
