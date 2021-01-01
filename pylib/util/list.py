# Copyright 2021, themeontology.org
# Tests:
"""
Create special lists of themes.
"""
import sys
import lib.dataparse
import lib.datastats
import lib.log
import lib.xls


def main():
    filename = sys.argv[-1]
    if "singletons" in sys.argv:
        #: themes that were used exactly once
        df = lib.dataparse.dataframe().reset_index()
        d = df[["sid", "theme"]].groupby("theme").agg("count")
        d_one = d[d["sid"] <= 1]
        df_one = df[df["theme"].isin(d_one.index)]
        lib.xls.write_themelist(df_one, filename)
    elif "forgotten":
        #: themes that were used more than ones but only in the early star trek series
        df = lib.dataparse.dataframe().reset_index()
        df["isearly"] = df["sid"].str[:3].isin(["tos", "tas", "tng", "ds9", "voy", "ent"])
        df2 = df[["theme", "isearly"]].groupby(["theme", "isearly"]).count().reset_index()
        d_late = df2[df2["isearly"]==False]["theme"]
        d = df[["sid", "theme"]].groupby("theme").agg("count")
        d_one = d[d["sid"] <= 1]
        df_early = df[~df["theme"].isin(d_late) & ~df["theme"].isin(d_one.index)]
        lib.xls.write_themelist(df_early, filename)
    else:
        lib.log.error("unknown command")

















