import sys
import os
import webdb
import lib.dataparse
import lib.xls
import re
from collections import defaultdict


def basic_convert(method, target):
    objs = []

    if method == "themedefs":
        m1 = "themes"
    elif method == "storydefs":
        m1 = "stories"
    elif method == "storythemes":
        m1 = "storythemes"

    if target == "<localdb>":
        m2 = 'db'
    elif target.endswith(".txt"):
        m2 = 'txt'
    elif target.endswith(".xls"):
        if method == "storythemes":
            m2 = 'xls_compact'
        else:
            m2 = 'xls'

    attr = "read_%s_from_%s" % (m1, m2)
    func = getattr(lib.dataparse, attr)
    objs = list(func() if m2 == "db" else func(target))
    txt = webdb.get_defenitions_text_for_objects(objs)

    print txt


def compact_sheet_full_convert(target):
    headers = [
        "StoryID",
        "Title",
        "Short Description",
        "Rating",
        "Main Characters",
        "Supporting Cast",
        "Genre",
        "Choice Theme", 
        "Major Theme",
        "Minor Theme",
    ]
    stuff, sheetcount, rowcount = lib.xls.read_xls(target, headers)
    visited = set()
    lines = []
        
    for row in sorted(stuff):
        topic = row[0]

        if topic in visited:
            raise ValueError, "Duplicate %s:" % headers[0], topic
        else:
            visited.add(topic)

        lines.append(topic)
        lines.append("=" * len(topic))
        lines.append("")

        for field, value in zip(headers[1:], row[1:]):
            lines.append(":: " + field)
            lines.append(value.strip())
            lines.append("")

        lines.append("")

    print "\n".join(l.encode("utf-8") for l in lines)


def expanded_theme_sheet_basic_convert(target):
    headers = [
        "StoryID",
        "Title",
        "Description",
        "FieldName",
        "Keyword",
        "Comment",
        "Related Characters",
        "Related Aliens", 
        "Named Thing",
    ]
    stuff, sheetcount, rowcount = lib.xls.read_xls(target, headers)
    themes = defaultdict(lambda: defaultdict(list))
    other = defaultdict(dict)

    for sid, title, description, fn, kw, com, relc, rela, nt in stuff:
        sid = sid.lower()
        capac = filter(None,
            [ x.strip() for x in relc.split(",") ] +
            [ x.strip() for x in rela.split(",") ] +
            [ x.strip() for x in nt.split(",") ]
        )
        entry = "%s [%s]" % (kw, com)
        if capac: 
            entry += " <%s>" % ", ".join(capac)
        fn = fn.strip() + "s"
        assert fn in [ "Minor Themes", "Major Themes", "Choice Themes", ]
        themes[sid][fn].append(entry)
        other[sid]["Title"] = title
        other[sid]["Description"] = description

    fieldorder = [ "Title", "Description", "Choice Themes", "Major Themes", "Minor Themes" ]
    lines = []

    for topic in sorted(other):
        lines.append(topic)
        lines.append("=" * len(topic))
        lines.append("")

        for field in fieldorder:
            if "Themes" in field:
                value = ",\n".join(themes[topic][field])
            else:
                value = other[topic][field]

            lines.append(":: " + field)
            lines.append(value.strip())
            lines.append("")

        lines.append("")

    print "\n".join(l.encode("utf-8") for l in lines)


def any_sheet_full_convert(target):
    """
    Convert any sheet into compact text format.
    One topic for each row using first column for naming.
    Then one field for each column, using column header as field name.
    """
    stuff, sheetcount, rowcount = lib.xls.read_xls(target)
    visited = set()
    lines = []
    headers = stuff[0]
        
    for row in sorted(stuff[1:]):
        topic = row[0]

        if topic in visited:
            raise ValueError, "Duplicate %s:" % headers[0], topic
        else:
            visited.add(topic)

        lines.append(topic)
        lines.append("=" * len(topic))
        lines.append("")

        for field, value in zip(headers[1:], row[1:]):
            lines.append(":: " + field)
            lines.append(value.strip())
            lines.append("")

        lines.append("")

    print "\n".join(l.encode("utf-8") for l in lines)


def any_sheet_extract_part(headers, rowregex, sheetregex, target):
    """
    Convert any sheet into compact text format.
    One topic for each row using first column for naming for topics matching regex.
    Then one field for each column, using column header as field name.
    """
    stuff, sheetcount, rowcount = lib.xls.read_xls(target, sheetname = sheetregex)
    visited = set()
    lines = []
    allheaders = stuff[0]

    if headers:
        headers = [ h.split("::") for h in headers ]
        renames = { hh[0]: hh[1] if len(hh) > 1 else hh[0] for hh in headers }
        headers = [ hh[0] for hh in headers ]
    else:
        renames = {}
        headers = allheaders

    hidxs = [ allheaders.index(hh) for hh in headers ]
    regex = re.compile(rowregex)
        
    for row in sorted(stuff[1:]):
        topic = row[0]

        if topic in visited:
            raise ValueError, "Duplicate %s:" % allheaders[0], topic
        else:
            visited.add(topic)

        if regex.match(topic):
            lines.append(topic)
            lines.append("=" * len(topic))
            lines.append("")

            for ii, header in enumerate(headers):
                idx = hidxs[ii]
                field = allheaders[idx]
                field = renames.get(field, field)
                value = row[idx]
                lines.append(":: " + field)
                lines.append(value.strip())
                lines.append("")

            lines.append("")

    print "\n".join(l.encode("utf-8") for l in lines)


def main():
    args = sys.argv
    fromidx = args.index("util.convert") + 1
    args = args[fromidx:]
    nargs = len(args)

    if nargs == 2:
        method = args[-2]
        target = os.path.abspath(args[-1])

        if method == "anysheet":
            any_sheet_full_convert(target)
        elif method == "compactsheet":
            compact_sheet_full_convert(target)
        elif method == "expandedthemes":
            expanded_theme_sheet_basic_convert(target)
        else:
            basic_convert(method, target)

    elif nargs == 5:
        method = args[0]
        headers = filter(None, [ x.strip() for x in args[1].split(",") ])
        rowregex = args[2]
        sheetregex = args[3]
        target = args[-1]

        if method == "extract":
            any_sheet_extract_part(headers, rowregex, sheetregex, target)



