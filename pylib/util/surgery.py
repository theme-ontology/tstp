import pandas as pd
import lib.dataparse


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
    df = lib.dataparse.dataframe().reset_index()
    dfp = df[df["theme"].isin(themes)]
    print(dfp)
    dfp.to_excel("temp.xls")


def main():
    alien_morals_list()




