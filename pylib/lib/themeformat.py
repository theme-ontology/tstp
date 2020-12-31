# Copyright 2020, themeontology.org
# Tests:
import lib.dataparse
from collections import defaultdict
import sys


FIELDRENAME = {
    "short description": "Description",
    "choice theme": "Choice Themes",
    "major theme": "Major Themes",
    "minor theme": "Minor Themes",
    "rating": "Ratings",
}


FIELDFORMATTERS = {
    "*": lambda lines: " ".join(x.strip() for x in lines),
    "description": lib.dataparse.block_fill,
    "examples": lib.dataparse.block_fill,
    "notes": lib.dataparse.block_fill,
    "choice themes": lib.dataparse.themejoin,
    "major themes": lib.dataparse.themejoin,
    "minor themes": lib.dataparse.themejoin,
}


FIELDORDER = [
    "Title",
    "Date",
    "Description",
    "Parents",
    "Notes",
    "Examples",
    "References",
    "Main Characters",
    "Supporting Cast",
    "Genre",
    "Ratings",
    "Choice Themes",
    "Major Themes",
    "Minor Themes",
]


def format_files(targets, banned=(), forced=(), extract=()):
    topics = defaultdict(dict)
    fieldorder = list(FIELDORDER)
    allfields = False
    found = set()

    for target in targets:
        stuff, notices = lib.dataparse.parse(target, subjects={}, default_parser=lib.dataparse.sanitize)

        for notice in notices:
            lib.log.error("%s: %s", target, notice)

        for topic, field, lines in stuff:
            field = FIELDRENAME.get(field.lower(), field)
            if field in banned:
                continue

            found.add(field)
            formater = (
                    FIELDFORMATTERS.get(field.lower(), None)
                    or (lambda lines: "\n".join(l.strip() for l in lines))
            )
            try:
                value = formater(lines)
            except AssertionError as exc:
                print >> sys.stderr, 'ERROR: ', target
                print >> sys.stderr, '.. in: ', topic, '::', field
                print >> sys.stderr, '..', str(exc)
                print >> sys.stderr, '.. SKIPPING!'
                continue

            topics[topic].setdefault(field, value)
            if field not in fieldorder:
                fieldorder.append(field)

    lines = []
    extracted = []
    for topic in sorted(topics):
        tgt = extracted if topic in extract else lines
        tgt.append(topic)
        tgt.append("=" * len(topic))
        tgt.append("")
        for field in fieldorder:
            if field in found:
                value = topics[topic].get(field, None)

                if allfields or field in forced or value is not None:
                    tgt.append(":: " + field)
                    if value:
                        tgt.append(value.strip())
                    tgt.append("")
        tgt.append("")

    return (lines, extracted) if extract else lines

