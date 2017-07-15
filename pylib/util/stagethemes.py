import sys
import log
import os
import re
import csv

from lib.files import walk


def expload_field( field ):
    '''
    Explode a field of raw data into quadruplets of (keyword,comment,implication,capacity).
    '''
    def dict2row( token ):
        kw = token.get( '', '' ).strip()
        com = token.get( '[', '' ).strip()
        imp = token.get( '{', '' ).strip()
        cap = token.get( '<', '' ).strip()
        return ( kw, com, imp, cap )
    
    token = {}
    delcorr = { '[':']', '{':'}', '<':'>' }
    farr = re.split( '([\[\]\{\}\<\>,])', field )
    state = ''
    
    for part in farr:
        if part in delcorr:
            state = part
        elif part in delcorr.values():
            if delcorr.get( state, None ) == part:
                state = ''
            else:
                raise AssertionError( 'Malformed field (bracket mismatch):\n  %s' % field )
        elif part == ',' and not state:
            tokrow = dict2row( token )
            if not tokrow[0].strip():
                raise AssertionError( 'Malformed field (empty keyword %s):\n  %s' % ( str( tokrow ), field ) )
            else:
                yield tokrow
            token = {}
        else:
            token[state] = token.get( state, '' ) + part
            
    tokrow = dict2row( token )
    if tokrow[0].strip():
        yield dict2row( token )


def parse_themes(txt):
    """
    parse a theme field.
    """
    field = " ".join(x.strip() for x in txt)
    for kw, comment, _implication, _capacity in expload_field(field):
        yield kw, comment


SUBJECTS = {
    "Ratings": lambda x: [],
    "Choice Themes": parse_themes,
    "Major Themes": parse_themes,
    "Minor Themes": parse_themes,
}


def parse(file):
    """
    Parse a file of themes and related info.
    """
    stories = []
    lines = []
    notices = []
    stuff = []

    # stories are delimeted by title underlined with ===
    with open(file, "r") as fh:
        for line in fh.readlines():
            if line.startswith("==="):
                stories.append(lines)
                lines = [ lines.pop() ]
            lines.append(line.strip())
    stories.append(lines)

    # subjects begin with "::", content may be parsed in different ways
    for lines in stories:
        title = lines[0]
        subject = None
        lineacc = []

        for idx, line in enumerate(lines):
            # hack to handle EOF
            if idx == len(lines) - 1:
                lineacc.append(line)
                line = ":: "

            # parse previous subject when subject changes
            if line.startswith(":: "):
                if subject in SUBJECTS:
                    parser = SUBJECTS[subject]

                    try:
                        stuff.append((title, subject, list(parser(lineacc))))
                    except Exception:
                        notices.append('Failed to parse data for "%s" in "%s"' % (subject, title))

                elif subject is not None:
                    notices.append('Unhandled subject "%s" in "%s"' % (subject, title))

                subject = line[3:].strip()
                lineacc = []

            # accumulate lines of subject
            else:
                lineacc.append(line)

    return stuff, notices


def write_table(file, headers, rows):
    """
    Produce a csv file woith some data.
    """
    with open(file, "wb") as fh:
        ww = csv.writer(fh, quoting = csv.QUOTE_MINIMAL)
        ww.writerow(headers)
        for row in rows:
            ww.writerow(row)
            print ":", row
    log.info('Wrote: %s.', file)


def main():
    target = os.path.abspath(sys.argv[-1])
    log.info("reading staged themes in: " + target + "...")
    themes = []
    errors = []

    for fpath in walk(target):
        rfpath = os.path.relpath(fpath, target)
        log.info("parsing %s", fpath)
        stuff, notices = parse(fpath)

        for notice in notices:
            log.warn("%s: %s", rfpath, notice)
            errors.append((rfpath, notice))

        for title, subject, contents in stuff:
            if subject.endswith("Themes"):
                for fields in contents:
                    themes.append((title, subject.strip("s"),) + fields + (rfpath,))

    write_table(
        os.path.join(target, "..", "notes_errors.csv"),
        ("file", "message"),
        errors,
    )
    write_table(
        os.path.join(target, "..", "notes_themes.csv"),
        ("Story", "FieldName", "Keyword", "Comment", "SourceFile"),
        themes,
    )
