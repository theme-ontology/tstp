"""
Read one or more text files and write their contents on stdout, while doing TO
specific cleaning and re-ordering.
"""
import sys
import os
import lib.dataparse
import lib.log
import codecs
import glob


FIELDS_RETAINED = [
    "Title",
    "Description",
    "Date",
    "Major Themes",
    "Collections",
    "Ratings",
    "Minor Themes",
    "Choice Themes",
    "Genre",
    "References",
    "Other Keywords",
    "Notes",
    "Authors",
    "Not Themes",
    "Related Stories",
    "Aliases",
    "Component Stories",
]


def order_key(obj):
    """
    Returns: key on which objects are to be ordered.
    """
    group = 0 if obj.name.lower().startswith("collection:") else 1
    return (group, obj.date)


def clean_blob(txt, retain=None, verbose=True):
    """
    Clean up a text blob of a single object.
    This may strip fields that are not recognized.
    """
    retain = retain or set(x.lower() for x in FIELDS_RETAINED)
    curfield = None
    lines = []
    for line in txt.split("\n"):
        if line.startswith(":: "):
            curfield = line[3:].strip().lower()
            if curfield not in retain:
                lib.log.warn("DROPPING FIELD: %s", line.strip())
        if not curfield or curfield in retain:
            lines.append(line)
    return "\n".join(lines).strip() + "\n\n"


def clean_merge_stdout():
    """
    Read from multiple files and write the cleaned combined ouput on stdout.
    """
    objects = []
    filetype = set()
    for target in filenames(sys.argv[2:]):
        filetype.add('.'.join(target.rsplit(".", 2)[-2:]))
        for obj in lib.dataparse.iter_stories_from_txt(target):
            objects.append(obj)
    if not len(filetype) == 1 or "--free" in sys.argv:
        raise RuntimeError("Can't combine files of different types: %s", sorted(filetype))
    for obj in sorted(objects, key=lambda o: o.date):
        print(clean_blob(obj.blob))


def filenames(argv):
    """
    List filenames implied by arguments (respecting globs).
    """
    for arg in sys.argv[2:]:
        if not arg.startswith("-"):
            for target in glob.glob(arg):
                yield os.path.abspath(target)


def main():
    """
    Entry point.
    """
    if "--merge" in sys.argv:
        return clean_merge_stdout()
    for target in filenames(sys.argv[2:]):
        objects = []
        for obj in lib.dataparse.iter_stories_from_txt(target):
            objects.append(obj)
        with codecs.open(target, "w", encoding='utf-8') as fh:
            for obj in sorted(objects, key=order_key):
                fh.write(clean_blob(obj.blob) + "\n")


