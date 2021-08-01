# Copyright 2021, themeontology.org
# Tests:
import themeontology
import glob
import sys
import pandas as pd
import lib.dataparse
import lib.xls
import lib.graph


def get_ontology():
    paths = set()
    for arg in sys.argv[2:-1]:
        for item in glob.glob(arg):
            paths.add(item)
    return themeontology.read(sorted(paths))


def main():
    to = get_ontology()
    data = []
    for story in to.stories():
        data.append([story.year, story.sid, story.title])
    data.sort()
    for year, sid, title in data:
        print(year, "::", sid, "::", title)