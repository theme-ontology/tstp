# Copyright 2021, themeontology.org
# Tests:
#   tests.test_themeontology
"""
This module shall contain all definitions required to parse data in
https://github.com/theme-ontology/theming and contain nothing that is not
required for that purpose.
"""
from __future__ import print_function
import os.path
import lib.files
import codecs
from collections import defaultdict


THEME_FIELD_CONFIG = {
    "Description": {
        "type": "text",
        "required": True,
    },
    "Parents": {"type": "list"},
    "References": {"type": "list"},
    "Examples": {"type": "text"},
    "Notes": {"type": "text"},
    "Aliases": {"type": "list"},
    "Template": {"type": "text"},
    "Other Parents": {"type": "text", "deprecated": True},
    "Related Themes": {"type": "text", "deprecated": True},
}

THEME_FIELD_ORDER = [
    "Description",
    "Parents",
    "Notes",
    "Examples",
    "References",
    "Aliases",
    "Template",
]

STORY_FIELD_CONFIG = {
    "Title": {"type": "text"},
    "Date": {"type": "date"},
    "Authors": {"type": "text"},
    "Variation": {"type": "text"},
    "Description": {"type": "text"},
    "References": {"type": "list"},
    "Ratings": {"type": "list"},
    "Choice Themes": {"type": "list"},
    "Major Themes": {"type": "list"},
    "Minor Themes": {"type": "list"},
    "Not Themes": {"type": "list"},
    "Other Keywords": {"type": "list"},
    "Collections": {"type": "list"},
    "Component Stories": {"type": "list"},
    "Genre": {"type": "text"},
    "Related Stories": {"type": "text"},
    "Notes": {"type": "text", "deprecated": True},
}

STORY_FIELD_ORDER = [
    "Title",
    "Date",
    "Description",
    "Authors",
    "Variation",
    "References",
    "Genre",
    "Collections",
    "Component Stories",
    "Related Stories",
    "Ratings",
    "Choice Themes",
    "Major Themes",
    "Minor Themes",
    "Not Themes",
    "Other Keywords",
]


class TOParser(object):
    @classmethod
    def iter_entries(cls, lines):
        """
        Iterate through the "entries" in a text file. An entry is a block of lines
        that starts with a title line, followed by a line starting with "===".
        Example entry:

            entry name
            ==========

            :: field 1
            data

            :: field 2
            data

        Args:
            lines: a file handle, or other generator of text strings.
        """
        linebuffer = []
        for line in lines:
            line = line.rstrip()
            if line.startswith("===") and linebuffer:
                prevlines = linebuffer[:-1]
                if any(x for x in prevlines):
                    yield prevlines
                linebuffer = [linebuffer[-1]]
            linebuffer.append(line)
        if linebuffer and any(line for line in linebuffer):
            yield linebuffer

    @classmethod
    def iter_fields(cls, lines):
        """
        Iterate through the fields of an entry. Fields are blocks starting with ::
        Args:
            lines: A list of strings.
        """
        linebuffer = []
        for line in lines:
            if line.startswith("::"):
                if linebuffer:
                    yield linebuffer
                linebuffer = [line]
            elif linebuffer:
                linebuffer.append(line)
        if linebuffer:
            yield linebuffer


class TOField(object):
    def __init__(self, lines=None):
        self.name = ""
        self.source = []
        self.data = []
        if lines:
            self.populate(lines)

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.data)
        )

    def populate(self, lines):
        """
        Interpret a list of text lines as a "field", assuming they conform
        to the required format.
        Args:
            lines: list of strings
        """
        self.source.extend(lines)
        self.name = lines[0].strip(": ")
        self.data = lines[1:]


class TOEntry(object):
    def __init__(self, lines=None):
        self.cfg = {}
        self.name = ""
        self.fields = []
        self.source = []
        if lines:
            self.populate(lines)

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.fields)
        )

    def iter_fields(self, reorder=False, skipunknown=False):
        """
        Iterate over the fields contained.
        Args:
            reorder: bool
                If True, use canonical order for fields.
            skipunknown: bool
                If True, omit deprecated and unknown fields.
        """
        lu = {f.name: f for f in self.fields}
        order = self.order if reorder else [f.name for f in self.fields]
        for fieldname in order:
            field = lu.get(fieldname, None)
            if field:
                if fieldname in self.cfg:
                    if skipunknown and self.cfg[fieldname].get("deprecated", False):
                        pass
                    else:
                        yield field

    def populate(self, lines):
        """
        Interpret a list of text lines as an "entry", assuming they conform
        to the required format.
        Args:
            lines:
        """
        self.source.extend(lines)
        cleaned = []
        for line in lines:
            cline = line.strip()
            if cline or (cleaned and cleaned[-1]):
                cleaned.append(cline)  # no more than one blank line in a row
        assert len(cleaned) > 1 and cleaned[1].startswith("==="), "missing name"
        while cleaned and not cleaned[-1]:
            cleaned.pop()
        self.name = cleaned[0]
        for fieldlines in TOParser.iter_fields(cleaned):
            while fieldlines and not fieldlines[-1]:
                fieldlines.pop()
            self.fields.append(TOField(fieldlines))

    def validate(self):
        for field in self.fields:
            if field.name not in self.cfg:
                yield u"{}: unknown field '{}'".format(self.name, field.name)


class TOTheme(TOEntry):
    def __init__(self, lines=None):
        super(TOTheme, self).__init__(lines=lines)
        self.cfg = THEME_FIELD_CONFIG
        self.order = THEME_FIELD_ORDER


class TOStory(TOEntry):
    def __init__(self, lines=None):
        super(TOStory, self).__init__(lines=lines)
        self.cfg = STORY_FIELD_CONFIG
        self.order = STORY_FIELD_ORDER


class ThemeOntology(object):
    def __init__(self, path):
        self.entries = defaultdict(list)
        self.read(path)

    def read(self, path):
        """
        Reads a file if path is a file name, or all files underneath a
        directory if path is a directory name.
        Args:
            path: a file or directory path
        """
        if os.path.isdir(path):
            for filepath in lib.files.walk(path, r".*\.(st|th)\.txt$"):
                self.read(filepath)
        else:
            entrytype = TOEntry
            if path.endswith(".th.txt"):
                entrytype = TOTheme
            elif path.endswith(".st.txt"):
                entrytype = TOStory
            with codecs.open(path, "r", encoding='utf-8') as fh:
                for entrylines in TOParser.iter_entries(fh):
                    entry = entrytype(entrylines)
                    self.entries[path].append(entry)

    def validate(self):
        """
        Yields warnings about recognized problems with the data.
        """
        for path, entries in self.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield u"{}: {}".format(path, warning)

    def write_clean(self):
        """
        Write the ontology back to its source file while cleaning up syntax and
        omitting unknown field names.
        """
        for path, entries in self.entries.items():
            print(path)
            lines = []
            for entry in entries:
                lines.extend([entry.name, "=" * len(entry.name), ""])
                for field in entry.iter_fields(reorder=False, skipunknown=True):
                    lines.extend(field.source)
                    lines.append("")
                lines.append("")
            with codecs.open(path, "w", encoding='utf-8') as fh:
                fh.writelines(x + "\n" for x in lines)


def read(path):
    return ThemeOntology(path)

