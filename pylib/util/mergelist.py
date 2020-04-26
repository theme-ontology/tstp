"""
Read themes entries from an Excel sheet and merge them into the repository.
"""
import sys
import lib.xls
import lib.log
from collections import defaultdict
import lib.files
from unidecode import unidecode


HEADERS = [
    "sid", "weight", "comment", "revised theme", "revised weight", "revised comment"
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
    data, sheetcount, rowcount = lib.xls.read_xls(filename, headers=HEADERS)
    lib.log.info("Read %s rows from %s sheets.", rowcount, sheetcount)
    return data


def main():
    themelist = defaultdict(list)
    entries = defaultdict(lambda: defaultdict(list))

    for sid, w, c, rt, rw, rc in read(sys.argv[2]):
        theme = rt.strip()
        weight = FIELDNAMES[rw.strip() or w]
        comment = rc.strip() or c
        if rt:
            entries[sid][weight].append([theme, comment])

    for path in lib.files.walk(sys.argv[3]):
        if path.endswith(".st.txt"):
            lib.log.debug("Reading %s...", path)
            lines, cursid, curfield, changed = [], None, None, False
            with open(path, "r") as fh:
                for line in fh:
                    line = line.decode('utf8')
                    if not line.strip() and cursid and curfield and not curfielddone:
                        for theme, comment in entries[cursid][curfield]:
                            theme = unidecode(theme)
                            themelist[(cursid, theme)].append(curfield)
                            lines.append("%s [%s],\n" % (theme, comment))
                            curfielddone = True  # mustn't add it again
                            changed = True
                    if line.startswith("==="):
                        cursid = lines[-1].strip()
                    elif line.startswith("::"):
                        curfield, curfielddone = line[2:].strip(), False
                    elif line.strip() and cursid and curfield and curfield.endswith(" Themes"):
                        theme = line.split("[")[0].strip()
                        themelist[(cursid, theme)].append(curfield)
                    lines.append(line)  # never drop any lines
            if changed:
                with open(path, "w") as fh:
                    for line in lines:
                        fh.write(line.encode("utf8"))

    for (sid, theme), fieldlist in themelist.items():
        if len(fieldlist) > 1:
            lib.log.warn("Multiple entries for %s in %s", (sid, theme), fieldlist)

