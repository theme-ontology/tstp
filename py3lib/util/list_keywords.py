# Copyright 2021, themeontology.org
# Tests:
import themeontology
import glob
import sys
import pandas as pd
import lib.dataparse
import lib.xls


def get_ontology():
    paths = set()
    for arg in sys.argv[2:-1]:
        for item in glob.glob(arg):
            paths.add(item)
    return themeontology.read(sorted(paths))


def main():
    filename = sys.argv[-1]
    to = get_ontology()
    data = []
    for story in to.stories():
        for entry in story.get("Other Keywords") or []:
            data.append([story.name, entry.keyword, entry])
    df = lib.dataparse.dataframe(subject="story").reset_index()
    df = df.set_index("sid")
    dfkws = pd.DataFrame(columns=["sid", "keyword", "entry"], data=data).set_index("sid")
    df = dfkws.join(df, on=["sid"], how="left").reset_index()
    print(df)
    columns = ["sid", "title", "story_def", "entry", "keyword", "DISCUSS", "revised comment", "revised theme", "revised weight",
               "revised capacity", "tentative action", "discussion thread", "MO notes"]
    lib.xls.write_themelist(df, filename, columns=columns)

