import pandas as pd
import lib.dataparse
import sys
from itertools import groupby


def triangle_infidelity_1():
    df2 = pd.read_excel("triangle-infidelity.xls")
    df = lib.dataparse.dataframe().reset_index()
    dfp = df[df["theme"] == u"extramarital affair"]
    df2.set_index("sid", inplace=True)
    dfp.set_index("sid", inplace=True)
    print(dfp.columns)
    dfp = dfp[["title", "story_def", "weight", "motivation"]].rename(
        columns={"weight": "eaweight", "motivation": "eamot"})
    dfr = df2.join(dfp, how="outer")
    print(dfr)
    dfr.to_excel("temp.xls")


def alien_morals_list():
    themes = ("alien morals", "alien customs", "conflict of moral codes", "cultural differences")
    df = makelist(themes, "temp.txt")
    print(df)
    df.to_excel("temp.txt")


def makelist(themes):
    df = lib.dataparse.dataframe().reset_index()
    return df[df["theme"].isin(themes)]


def makejoined(dfs):
    if len(dfs) > 1:
        for idx, df in list(enumerate(dfs)):
            if idx > 0:
                df = df[["sid", "theme", "weight", "motivation"]]
            df = df.rename(columns={"theme": "theme" + str(idx), "weight": "weight" + str(idx), "motivation": "motivation" + str(idx)})
            df.set_index("sid", inplace=True)
            dfs[idx] = df
    dfacc = dfs[0]
    for df in dfs[1:]:
        dfacc = dfacc.join(df, on=["sid"], how="outer")
    return dfacc


def main():
    args = sys.argv[sys.argv.index("util.surgery")+1:]
    if len(args) <= 1:
        raise ValueError("not enough arguments")
    filename = args[-1]
    themes = args[:-1]
    dfs = [makelist(tl) for k, tl in groupby(themes, lambda x: x == "--") if not k]
    df = makejoined(dfs)
    print(df)
    df.to_excel(filename)




