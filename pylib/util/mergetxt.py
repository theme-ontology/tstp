"""
Merge different txt files with data in our special format together into one.
Some fields (themes, descriptions) will have predefined formating.
Priority is given to fields early in the list of files.
"""
import sys
import os
import webdb
import lib.dataparse
import lib.xls
from collections import defaultdict
import textwrap


def block_fill(lines):
    paragraphs = lib.dataparse.blockjoin(lines)
    lines = []

    for txt in paragraphs.split("\n\n"):
        lines.append(textwrap.fill(txt, 78))
        lines.append("")

    return "\n".join(lines)


FIELDRENAME = {
    "short description": "Description",
    "choice theme": "Choice Themes",
    "major theme": "Major Themes",
    "minor theme": "Minor Themes",
    "rating": "Ratings",
}


FIELDFORMATTERS = {
    "*": lambda lines: " ".join(x.strip() for x in lines),
    "description": block_fill,
    "choice themes": lib.dataparse.themejoin,
    "major themes": lib.dataparse.themejoin,
    "minor themes": lib.dataparse.themejoin,
}


FIELDORDER = [
    "Title",
    "Description",
    "Ratings",
    "Main Characters",
    "Supporting Cast",
    "Genre",
    "Choice Themes",
    "Major Themes",
    "Minor Themes",
]


def main():
    topics = defaultdict(dict)
    fieldorder = list(FIELDORDER)

    for arg in sys.argv[2:]:
        if arg.startswith("-"):
            continue

        target = os.path.abspath(arg)
        stuff, notices = lib.dataparse.parse(target, {})

        for notice in notices:
            lib.log.error("%s: %s", target, notice)

        for topic, field, lines in stuff:
            field = FIELDRENAME.get(field.lower(), field)
            formater = (
                FIELDFORMATTERS.get(field.lower(), None) 
                or (lambda lines: "\n".join(l.strip() for l in lines))
            )

            try:
                value = formater(lines)
            except AssertionError as exc:
                print >>sys.stderr, 'ERROR: ', arg
                print >>sys.stderr, '.. in: ', topic, '::', field
                print >>sys.stderr, '..', str(exc)
                print >>sys.stderr, '.. SKIPPING!'
                continue

            topics[topic].setdefault(field, value)
            if field not in fieldorder:
                fieldorder.append(field)

    lines = []

    for topic in sorted(topics):
        lines.append(topic)
        lines.append("=" * len(topic))
        lines.append("")

        for field in fieldorder:
            value = topics[topic].get(field, None)

            if value is not None:
                lines.append(":: " + field)
                lines.append(value.strip())
                lines.append("")
                
        lines.append("")

    print "\n".join(l.encode("utf-8") for l in lines)

