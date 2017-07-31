import sys
import log
import os
import re
import csv
from collections import defaultdict

from lib.files import walk
from lib.dataparse import expload_field
import webobject


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

    # stories are delimeted by story-id underlined with ===
    with open(file, "r") as fh:
        for line in fh.readlines():
            if line.startswith("==="):
                stories.append(lines)
                lines = [ lines.pop() ]
            lines.append(line.strip())
    stories.append(lines)

    # subjects begin with "::", content may be parsed in different ways
    for lines in stories:
        storyid = lines[0]
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
                        stuff.append((storyid, subject, list(parser(lineacc))))
                    except Exception:
                        notices.append('Failed to parse data for "%s" in "%s"' % (subject, storyid))

                elif subject is not None:
                    notices.append('Unhandled subject "%s" in "%s"' % (subject, storyid))

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
        ww = csv.writer(fh, quoting = csv.QUOTE_MINIMAL, lineterminator = "\n")
        ww.writerow(headers)
        for row in rows:
            ww.writerow(row)
    log.info('Wrote: %s.', file)


def main():
    target = os.path.abspath(sys.argv[-1])
    log.info("reading staged themes in: " + target + "...")

    all_themes = set(th.name for th in webobject.Theme.load())
    all_stories = set(st.name for st in webobject.Story.load())
    undef_themes = defaultdict(list)
    undef_stories = defaultdict(list)
    themes = []
    errors = []
    undef_theme_rows = []
    undef_story_rows = []

    # parse all the files
    for fpath in walk(target, ".*-stories.txt"):
        rfpath = os.path.relpath(fpath, target)
        log.info("parsing %s", fpath)
        stuff, notices = parse(fpath)

        for notice in notices:
            log.warn("%s: %s", rfpath, notice)
            errors.append((rfpath, notice))

        for storyid, subject, contents in stuff:
            if storyid not in all_stories:
                undef_stories[storyid].append(rfpath)

            if subject.endswith("Themes"):
                for fields in contents:
                    theme = fields[0]
                    themes.append((storyid, subject.strip("s"),) + fields + (rfpath,))

                    if theme not in all_themes:
                        undef_themes[theme].append("%s: %s [%s]" % (rfpath, storyid, subject))

    # collate undefined themes and stories
    for theme, refs in undef_themes.iteritems():
        undef_theme_rows.append((theme, "", "", "", "", ", ".join(refs)))
    for sid, refs in undef_stories.iteritems():
        undef_story_rows.append((sid, "", "", "", ", ".join(sorted(set(refs)))))

    # write tables of results
    write_table(
        os.path.join(target, "..", "auto", "notes_errors.csv"),
        ("file", "message"),
        errors,
    )
    write_table(
        os.path.join(target, "..", "auto", "notes_themes.csv"),
        ("Story", "FieldName", "Keyword", "Comment", "SourceFile"),
        themes,
    )
    write_table(
        os.path.join(target, "..", "auto", "notes_undefined_themes.csv"),
        ("Keyword", "Implications", "RelatedThemes", "Definition", "Example", "References"),
        undef_theme_rows,
    )
    write_table(
        os.path.join(target, "..", "auto", "notes_undefined_stories.csv"),
        ("StoryID", "Title", "ReleaseDate", "Description", "References"),
        undef_story_rows,
    )
