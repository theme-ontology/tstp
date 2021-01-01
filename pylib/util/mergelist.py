"""
Read themes entries from an Excel sheet and merge them into the repository.
"""
import sys
import lib.xls
import lib.log
from collections import defaultdict
import lib.files
from unidecode import unidecode
from pprint import pprint
import lib.dataparse


HEADERS = [
    "sid", "weight", "theme", "motivation", "revised theme", "revised weight", "revised comment", "revised capacity"
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
    lib.log.info("Reading named columns from %s: %s", filename, HEADERS)
    data, sheetcount, rowcount = lib.xls.read_xls(filename, headers=HEADERS, sheetname="data")
    lib.log.info("Read %s rows from %s sheets.", rowcount, sheetcount)
    if sheetcount < 1:
        lib.log.warn("Found no sheet named 'data'. Expected one!")
    return data


def format_line(theme, comment, capacity):
    """
    Format a theme entry line.
    """
    if capacity:
        return "%s <%s> [%s],\n" % (theme, capacity, comment)
    else:
        return "%s [%s],\n" % (theme, comment)


def main():
    """
    pyrun util.mergelist mydata.xlsx ./notes
    """
    themelist = defaultdict(list)
    newentries = defaultdict(lambda: defaultdict(list))
    replacements = defaultdict(list)
    deletions = defaultdict(bool)
    old_themes = set(obj.name for obj in lib.dataparse.read_themes_from_repo())
    new_themes = defaultdict(list)

    for sid, w, t, c, rt, rw, rc, rcap in read(sys.argv[2]):
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
        if oldtheme:
            deletions[(sid, oldweight, oldtheme)] = True
            if theme:
                if oldweight == weight:
                    replacements[(sid, oldweight, oldtheme)].append((weight, theme, comment, capacity))
                else:
                    newentries[sid][weight].append([theme, comment, capacity])
        elif theme:
            newentries[sid][weight].append([theme, comment, capacity])

    if '--test' in sys.argv:
        print("NEW")
        for sid in newentries:
            print(sid)
            pprint(dict(newentries[sid]))
        print("REPLACEMENT")
        pprint(dict(replacements))
        print("DELETION")
        pprint(dict(deletions))
        return

    for path in lib.files.walk(sys.argv[3]):
        if path.endswith(".st.txt"):
            lib.log.debug("Reading %s...", path)
            lines, cursid, curfield, changed = [], None, None, False
            with open(path, "r") as fh:
                for line in fh:
                    line = line.decode('utf8')
                    deleteit = False

                    # parse each line, understand flow and delete/replace themes
                    if line.startswith("==="):
                        cursid = lines[-1].strip()
                    elif line.startswith("::"):
                        curfield, curfielddone = line[2:].strip(), False
                    elif line.strip() and cursid and curfield and curfield.endswith(" Themes"):
                        theme = line.split("[")[0].strip()
                        key = (cursid, curfield, theme)

                        # delete theme and insert replacements?
                        if key in deletions:
                            changed = True
                            deleteit = True
                            for nw, nt, nc, ncapacity in replacements[key]:
                                newtheme = unidecode(nt)
                                newcomment = unidecode(nc)
                                ncapacity = unidecode(ncapacity)
                                themelist[(cursid, newtheme)].append(curfield)
                                lines.append(format_line(newtheme, newcomment, ncapacity))
                            replacements[key] = []
                        else:
                            themelist[(cursid, theme)].append(curfield)

                    # add new themes at end of field
                    if not line.strip() and cursid and curfield and not curfielddone:
                        curfielddone = True  # mustn't do this more than once
                        for key in replacements:
                            if key[:2] == (cursid, curfield):
                                for nw, nt, nc, ncapacity in replacements[key]:
                                    lib.log.warn("REPLACEMENT TARGET MISSING, APPENDING: %s -> %s", key, nt)
                                    newtheme = unidecode(nt)
                                    newcomment = unidecode(nc)
                                    ncapacity = unidecode(ncapacity)
                                    themelist[(cursid, newtheme)].append(curfield)
                                    lines.append(format_line(newtheme, newcomment, ncapacity))
                                    changed = True
                        for theme, comment, ncapacity in newentries[cursid][curfield]:
                            theme = unidecode(theme)
                            themelist[(cursid, theme)].append(curfield)
                            ncapacity = unidecode(ncapacity)
                            lines.append(format_line(theme, comment, ncapacity))
                            changed = True

                    # unless explicitly deleted, add back just as it was
                    if not deleteit:
                        lines.append(line)

            if changed:
                with open(path, "w") as fh:
                    for line in lines:
                        fh.write(line.encode("utf8"))
                        #print(line.encode("ascii", "ignore"))

    for (sid, theme), fieldlist in themelist.items():
        if len(fieldlist) > 1:
            lib.log.warn("Multiple entries for %s in %s", (sid, theme), fieldlist)

    for newtheme, previous in new_themes.items():
        lib.log.warn("Undefined New Theme: %s CHANGED FROM %s", newtheme, sorted(set(previous)))



