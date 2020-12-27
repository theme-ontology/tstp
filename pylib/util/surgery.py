import pandas as pd
import lib.dataparse
import sys
from itertools import groupby
from collections import defaultdict


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


def get_descendents(children, ancestor):
    """
    Returns:
    A list of all children, children of children, etc. for a list of ancestor themes.
    """
    found = set()
    pending = set(children[ancestor])
    while pending:
        th = pending.pop()
        if th not in found:
            found.add(th)
            pending.update(children[th])
    return found


def parse_themes(args):
    """
    Args:
        args: sys.argv, or segment thereof

    Returns:
        list of themes
    """
    themeobjs = list(lib.dataparse.read_themes_from_repo())
    themes = []
    flag = ""
    children = defaultdict(list)

    for tobj in themeobjs:
        for parent in tobj.list_parents():
            children[parent].append(tobj.name)

    for arg in args:
        if arg.startswith("-"):
            flag = arg
        else:
            themes.append(arg)
            print("+ %s" % arg)
            if flag == "-co":
                print("children of of '%s':" % arg)
                for obj in themeobjs:
                    if arg in obj.list_parents():
                        themes.append(obj.name)
                        print("  + %s" % obj.name)
            if flag == "-do":
                print("descendents of of '%s':" % arg)
                desc = get_descendents(children, arg)
                for obj in themeobjs:
                    if obj.name in desc:
                        themes.append(obj.name)
                        print("  + %s" % obj.name)
            flag = ""

    return sorted(set(themes))


def main():
    args = sys.argv[sys.argv.index("util.surgery")+1:]
    show_raw_columns = "--raw" in args
    if len(args) <= 1:
        raise ValueError("not enough arguments")
    filename = args[-1]
    themes = parse_themes(args[:-1])
    dfs = [makelist(tl) for k, tl in groupby(themes, lambda x: x == "--") if not k]
    df = makejoined(dfs)
    print(df)

    if show_raw_columns:
        df.to_excel(filename)
    else:
        REVIEW_COLS = ["sid", "title", "parents", "theme", "weight", "motivation", "DISCUSS", "revised comment",
                       "revised theme", "revised weight", "tentative action", "discussion thread", "MO notes"]
        REVIEW_COL_WIDTHS = {'weight':10, 'motivation': 40, 'revised comment': 40}

        for col in REVIEW_COLS:
            if col not in df.columns:
                df[col] = ""

        writer = pd.ExcelWriter(filename, engine="xlsxwriter")
        df.to_excel(writer, columns=REVIEW_COLS, header=True, index=False, freeze_panes=(1,1), sheet_name="data")
        workbook = writer.book
        worksheet = writer.sheets['data']
        worksheet.set_default_row(70)
        basic = {
            'text_wrap': True,
            'valign': 'vcenter',
            'align': 'left',
            'border': 1,
            'border_color': '#cccccc',
        }
        revise = dict(basic, **{
            'bg_color': '#ffffcc'
        })
        format_basic = workbook.add_format(basic)
        format_revise = workbook.add_format(revise)

        for idx, colname in enumerate(REVIEW_COLS):
            width = REVIEW_COL_WIDTHS.get(colname, 15)
            colc = chr(ord("A")+idx)
            fmt = format_revise if 7 <= idx <= 9 else format_basic
            worksheet.set_column('{}:{}'.format(colc, colc), width, fmt)

        writer.save()


