"""
Read themes entries from an Excel sheet and merge them into the repository.
"""
import sys
import lib.xls
import lib.log
from collections import defaultdict
import lib.files
from pprint import pprint
import lib.dataparse
import themeontology


REQUIRED_HEADERS = [
    "sid", "weight", "theme", "motivation", "revised theme", "revised weight", "revised comment"
]
OPTIONAL_HEADERS = [
    "revised capacity"
]
FIELDNAMES = {
    "minor": "Minor Themes",
    "major": "Major Themes",
    "choice": "Choice Themes",
}

def read(filename):
    """
    Read required columns from an excel file.
    """
    headers = lib.xls.get_headers(filename, sheetpattern="data")[0][1]
    for hh in REQUIRED_HEADERS:
        if hh not in headers:
            lib.log.error("missing header: %s", hh)
    activeheaders = list(REQUIRED_HEADERS)
    for hh in OPTIONAL_HEADERS:
        if hh in headers:
            activeheaders.append(hh)
    lib.log.info("Reading named columns from %s: %s", filename, activeheaders)
    data, sheetcount, rowcount = lib.xls.read_xls(filename, headers=activeheaders, sheetname="data")
    lib.log.info("Read %s rows from %s sheets.", rowcount, sheetcount)
    if sheetcount < 1:
        lib.log.warn("Found no sheet named 'data'. Expected one!")
    return activeheaders, data


def format_line(theme, comment, capacity):
    """
    Format a theme entry line.
    """
    if capacity:
        return "%s <%s> [%s]\n" % (theme, capacity, comment)
    else:
        return "%s [%s]\n" % (theme, comment)


def get_changes(listpath):
    """
    Read desired changes from excel file.
    Returns:
    """
    old_themes = set(obj.name for obj in lib.dataparse.read_themes_from_repo())
    activeheaders, data = read(listpath)
    do_capacity = "revised capacity" in activeheaders
    newentries = defaultdict(lambda: defaultdict(list))
    replacements = defaultdict(list)
    deletions = defaultdict(bool)
    new_themes = defaultdict(list)
    for row in data:
        sid, w, t, c, rt, rw, rc = row[:7]
        rcap = row[7] if do_capacity else ""
        sid = sid.strip()
        oldtheme = t.strip()
        theme = rt.strip()
        oldweight = FIELDNAMES.get(w.strip(), "")
        weight = FIELDNAMES.get(rw.strip() or w.strip(), "")
        comment = rc.strip() or c
        capacity = rcap.strip()
        if theme and theme not in old_themes:
            new_themes[theme].append(oldtheme)
        if not sid:
            continue  ## blank rows at end, maybe
        if not weight:
            lib.log.warn("MISSING WEIGHT IN ENTRY %s - SKIPPING", (sid, w, t, rt, rw))
            continue
        if oldtheme and oldweight:
            deletions[(sid, oldweight, oldtheme)] = True
            if theme:
                if oldweight == weight:
                    replacements[(sid, oldweight, oldtheme)].append((weight, theme, comment, capacity))
                else:
                    newentries[sid][weight].append([theme, comment, capacity])
        elif theme:
            newentries[sid][weight].append([theme, comment, capacity])

    return newentries, replacements, deletions, new_themes


def report_changes(newentries, replacements, deletions, new_themes):
    """
    Just print a summary of changes for debugging.
    """
    print("NEW")
    for sid in newentries:
        print(sid)
        pprint(dict(newentries[sid]))
    print("REPLACEMENT")
    pprint(dict(replacements))
    print("DELETION")
    pprint(dict(deletions))

    for newtheme, previous in new_themes.items():
        lib.log.warn("Undefined New Theme: %s CHANGED FROM %s", newtheme, sorted(set(previous)))


def new_mergelist(listpath, notespath):
    themelist = defaultdict(list)
    newentries, replacements, deletions, new_themes = get_changes(listpath)
    if '--test' in sys.argv:
        return report_changes(newentries, replacements, deletions, new_themes)
    to = themeontology.read()

    # delete keywords and replace if needed
    for key in deletions:
        (sid, oldweight, oldtheme) = key
        kwfield = to.story[sid].get(oldweight)
        idx = kwfield.delete(oldtheme)
        for nw, nt, nc, ncapacity in replacements[key]:
            assert oldweight == nw, "replacement listed but weights don't match, illogical"
            kwfield.insert(idx, nt, nc, ncapacity)  ## {notes} not supported yet
        del replacements[key]

    # add remaining replacements, if any
    for key in replacements:
        (sid, oldweight, oldtheme) = key
        kwfield = to.story[sid].get(oldweight)
        for nw, nt, nc, ncapacity in replacements[key]:
            lib.log.warn("REPLACEMENT TARGET MISSING, APPENDING: %s -> %s", key, nt)
            assert oldweight == nw, "replacement listed but weights don't match, illogical"
            kwfield.insert(None, nt, nc, ncapacity)

    for sid in newentries:
        for fieldname in newentries[sid]:
            for theme, comment, ncapacity in newentries[sid][fieldname]:
                kwfield = to.story[sid].get(fieldname)
                kwfield.insert(None, theme, comment, ncapacity)

    to.write_clean()


def main():
    """
    pyrun util.mergelist mydata.xlsx ./notes
    """
    #old_mergelist(sys.argv[2], sys.argv[3])
    new_mergelist(sys.argv[2], sys.argv[3])
