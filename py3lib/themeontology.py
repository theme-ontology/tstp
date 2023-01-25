# Copyright 2021, themeontology.org
# Tests:
#   tests.test_themeontology
"""
This module shall contain all definitions required to parse data in
https://github.com/theme-ontology/theming and contain nothing that is not
required for that purpose.
"""
import codecs
import os.path
import re
from collections import defaultdict

import lib.files
import lib.textformat


THEME_FIELD_CONFIG = {
    "Description": {"type": "text", "required": True},
    "Parents": {"type": "list"},
    "References": {"type": "list"},
    "Examples": {"type": "text"},
    "Notes": {"type": "text"},
    "Aliases": {"type": "list"},
    "Template": {"type": "blob"},
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
    "Authors": {"type": "blob"},
    "Variation": {"type": "blob"},
    "Description": {"type": "text"},
    "References": {"type": "list"},
    "Ratings": {"type": "list"},
    "Choice Themes": {"type": "kwlist"},
    "Major Themes": {"type": "kwlist"},
    "Minor Themes": {"type": "kwlist"},
    "Not Themes": {"type": "kwlist"},
    "Other Keywords": {"type": "kwlist"},
    "Collections": {"type": "list"},
    "Component Stories": {"type": "list"},
    "Related Stories": {"type": "list"},
}

STORY_FIELD_ORDER = [
    "Title",
    "Date",
    "Description",
    "Authors",
    "Variation",
    "References",
    "Genre",
    "Ratings",
    "Collections",
    "Component Stories",
    "Related Stories",
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

    @classmethod
    def iter_listitems(cls, lines):
        """
        Turn a list of strings into items. Items may be newline or comma separated.
        Args:
            lines: list of strings
        """
        for line in lines:
            # note: once upon a time we used to have multiple items separated by commas on a single line
            # but that is no longer permitted.
            item = line.strip()
            if item:
                yield item

    @classmethod
    def iter_kwitems(cls, lines):
        """
        Turn a list of strings into kewyword items. Items may be newline or comma separated.
        Items may contain data in () [] {} parentheses.
        Args:
            lines: list of strings
        """
        def dict2row(tokendict):
            tkw = tokendict.get('', '').strip()
            tmotivation = tokendict.get('[', '').strip()
            tcapacity = tokendict.get('<', '').strip()
            tnotes = tokendict.get('{', '').strip()
            return tkw, tcapacity, tmotivation, tnotes

        field = '\n'.join(lines)
        token = {}
        delcorr = {'[': ']', '{': '}', '<': '>'}
        farr = re.split('([\[\]\{\}\<\>,\\n])', field)
        state = ''
        splitters = ',\n'

        for part in farr:
            if part in delcorr:
                state = part
            elif part in delcorr.values():
                if delcorr.get(state, None) == part:
                    state = ''
                else:
                    raise AssertionError('Malformed field (bracket mismatch):\n  %s' % field)
            elif part in splitters and not state:
                tokrow = dict2row(token)
                if not tokrow[0].strip():
                    #raise AssertionError('Malformed field (empty keyword %s):\n  %s' % (str(tokrow), field))
                    pass  # possible now that we allow splitting by both newline and comma
                else:
                    yield tokrow
                token = {}
            else:
                token[state] = token.get(state, '') + part

        tokrow = dict2row(token)
        if tokrow[0].strip():
            yield dict2row(token)


class TOKeyword(object):
    def __init__(self, keyword, capacity=None, motivation=None, notes=None):
        self.keyword = keyword
        self.motivation = motivation
        self.capacity = capacity
        self.notes = notes
        assert(len(keyword.strip()) > 0)

    def __str__(self):
        pm = u" [{}]".format(self.motivation) if self.motivation else ""
        pc = u" <{}>".format(self.capacity) if self.capacity else ""
        pn = u" {{{}}}".format(self.notes) if self.notes else ""
        return u"{}{}{}{}".format(self.keyword, pc, pm, pn)

    def __repr__(self):
        return 'TOKeyword<{}>'.format(str(self))


class TOField(object):
    def __init__(self, lines=None, fieldconfig=None, name=''):
        self.name = name
        self.source = []
        self.data = []
        self.fieldconfig = fieldconfig or {}
        self.parts = []
        if lines:
            self.populate(lines)

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.data)
        )

    def __str__(self):
        return self.text_canonical_contents()

    def __iter__(self):
        for part in self.iter_parts():
            yield part

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
        self.parts = []
        fieldtype = self.fieldconfig.get("type", "blob")
        if fieldtype == "kwlist":
            for kwtuple in TOParser.iter_kwitems(self.data):
                self.parts.append(TOKeyword(*kwtuple))
        elif fieldtype == "list":
            for item in TOParser.iter_listitems(self.data):
                self.parts.append(item)
        elif fieldtype == "text":
            self.parts.append(lib.textformat.add_wordwrap("\n".join(self.data)).strip())
        else:
            self.parts.append('\n'.join(self.data))

    def iter_parts(self):
        """
        Iterater over components in the data of this field.
        """
        for part in self.parts:
            yield part

    def text_canonical_contents(self):
        """
        Returns:
            A text blob representing the contents of this field in its canonical format.
        """
        parts = [str(x) for x in self.iter_parts()]
        return u'\n'.join(parts)

    def text_canonical(self):
        """
        Returns:
            A text blob representing this field in its canonical format.
        """
        parts = [u":: {}".format(self.name)]
        parts.extend(str(x) for x in self.iter_parts())
        return u'\n'.join(parts)

    def delete(self, kw):
        """
        Delete a keyword.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        todelete = set()
        if fieldtype == "kwlist":
            for idx, part in enumerate(self.parts):
                if part.keyword == kw:
                    todelete.add(idx)
        self.parts = [p for idx, p in enumerate(self.parts) if idx not in todelete]
        return min(todelete) if todelete else len(self.parts)

    def update(self, kw, keyword=None, motivation=None, capacity=None, notes=None):
        """
        Update keyword data.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        if fieldtype == "kwlist":
            for part in self.parts:
                if part.keyword == kw:
                    if keyword is not None:
                        part.keyword = keyword
                    if motivation is not None:
                        part.motivation = motivation
                    if capacity is not None:
                        part.capacity = capacity
                    if notes is not None:
                        part.notes = notes

    def insert(self, idx=None, keyword="", motivation="", capacity="", notes=""):
        """
        Insert a new keyword at location idx in the list.
        If idx is None, append.
        """
        if idx is None:
            idx = len(self.parts)
        self.parts.insert(idx, TOKeyword(keyword, capacity=capacity, motivation=motivation, notes=notes))


class TOEntry(object):
    cfg = None
    order = None
    def __init__(self, lines=None):
        self.cfg = self.cfg or {}
        self.order = self.order or []
        self.name = ""
        self.fields = []
        self.source = []
        self.parents = []
        self.children = []
        self.links = []
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
            lines: list of strings
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
            name = fieldlines[0].strip(": ")
            fieldconfig = self.cfg.get(name, {})
            self.fields.append(TOField(fieldlines, fieldconfig))

    def setup(self):
        """
        This should be called after the ontology has been populated, to link entries
        to each other where appropriate.
        """
        pass

    def validate(self):
        """
        Report on problems with the syntax of the entry.
        Returns:
            yields warnings as strings.
        """
        junklines = []
        for idx, line in enumerate(self.source):
            if idx > 1:
                if line.startswith("::"):
                    break
                elif line.strip():
                    junklines.append(line)
        if junklines:
            junkmsg = '/'.join(junklines)
            if len(junkmsg) > 13:
                junkmsg = junkmsg[:10] + "..."
            yield u"{}: junk in entry header: {}".format(self.name, junkmsg)
        for field in self.fields:
            if field.name not in self.cfg:
                yield u"{}: unknown field '{}'".format(self.name, field.name)

    def text_canonical(self):
        """
        Returns:
            A text blob representing this entry in its canonical format.
        """
        lines = [self.name, "=" * len(self.name), ""]
        for field in self.iter_fields(reorder=True, skipunknown=True):
            lines.append(field.text_canonical())
            lines.append("")
        return "\n".join(lines)

    def get(self, fieldname):
        """
        Returns:
        The field named fieldname, if there is one.
        """
        for field in self.fields:
            if field.name == fieldname:
                return field
        fieldconfig = self.cfg.get(fieldname, {})
        self.fields.append(TOField([], fieldconfig, name=fieldname))
        return self.fields[-1]


class TOTheme(TOEntry):
    def __init__(self, lines=None):
        self.cfg = THEME_FIELD_CONFIG
        self.order = THEME_FIELD_ORDER
        super(TOTheme, self).__init__(lines=lines)

    def setup(self):
        """
        This should be called after the ontology has been populated, to link entries
        to each other where appropriate.
        """
        pass

    def verbose_description(self):
        """
        A description that combines various other fields, including Notes, Examples,
        Aliases, and References.
        """
        description = str(self.get("Description"))
        examples = str(self.get("Examples")).strip()
        aliases = str(self.get("Aliases")).strip()
        notes = str(self.get("Notes")).strip()
        references = str(self.get("References")).strip()
        if notes:
            description += "\n\nNotes:\n" + notes
        if examples:
            description += "\n\nExamples:\n" + examples
        if aliases:
            description += "\n\nAliases:\n" + aliases
        if references:
            description += "\n\nReferences:\n"
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    description += line + "\n"
        return description

    def html_description(self):
        """
        Turn the verbose description into html.
        """
        import html
        description = html.escape(str(self.get("Description")))
        examples = html.escape(str(self.get("Examples")).strip())
        aliases = html.escape(str(self.get("Aliases")).strip())
        notes = html.escape(str(self.get("Notes")).strip())
        references = html.escape(str(self.get("References")).strip())
        description = '<P class="obj-description"><BR>\n' + description
        description += "</P>\n"
        if notes:
            description += '<P class="obj-description"><b>Notes:</b><BR>\n' + notes
            description += "</P>\n"
        if examples:
            description += '<P class="obj-description"><b>Examples:</b><BR>\n' + examples
            description += "</P>\n"
        if aliases:
            description += '<P class="obj-description"><b>Aliases:</b><BR>\n' + aliases
            description += "</P>\n"
        if references:
            description += '<P class="obj-description"><b>References:</b><BR>\n'
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    aline = '<A href="{}">{}</A>'.format(line, line)
                    description += aline + "\n"
            description += "</P>\n"
        return description

    def html_short_description(self):
        """
        A limited length short description without embelishments like "references".
        """
        import html
        description = str(self.get("Description"))[:256]
        return html.escape(description)


class TOStory(TOEntry):
    def __init__(self, lines=None):
        self.cfg = STORY_FIELD_CONFIG
        self.order = STORY_FIELD_ORDER
        super(TOStory, self).__init__(lines=lines)

    def iter_theme_entries(self):
        """
        Yield (weight, TOTheme) pairs.
        """
        for weight in ["Choice Themes", "Major Themes", "Minor Themes", "Not Themes"]:
            field = self.get(weight)
            if field:
                for part in field.iter_parts():
                    yield weight, part

    @property
    def date(self):
        """
        Return the date entry as verbatim it is recorded in the text file.
        """
        return self.get("Date").text_canonical_contents().strip()

    @property
    def year(self):
        """
        Returns the year of the story, or the earliest year for a collection.
        A positive number is the year AD.
        A negative number is the year BC.
        Zero indicates that the the information is missing (there is no year zero in AD/BC notation).
        Dates can be entered in a variety of ways but the year should always be present.
        If this function returns zero for a story the story's data entry is considered to be faulty.
        """
        date = self.date
        yearmatch = re.match("\d+", date)
        if not yearmatch:
            return 0
        year = int(yearmatch.group())
        if "bc" in date.lower():
            year *= -1
        return year

    @property
    def sid(self):
        """
        Shorthand for Story ID, ie. the name of the entry when the entry is a story entry.
        """
        return self.name

    @property
    def title(self):
        """
        The title of the story.
        This should always be present or the data entry is faulty.
        """
        return self.get("Title").text_canonical_contents().strip()

    def verbose_description(self):
        """
        A description that combines various other fields, including Notes, Examples,
        Aliases, and References.
        """
        description = str(self.get("Description"))
        references = str(self.get("References")).strip()
        if references:
            description += "\n\nReferences:\n"
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    description += line + "\n"
        return description

    def html_description(self):
        """
        Turn the verbose description into html.
        """
        import html
        description = html.escape(str(self.get("Description")))
        references = html.escape(str(self.get("References")).strip())
        description = '<P class="obj-description"><BR>\n' + description
        description += "</P>\n"
        if references:
            description += '<P class="obj-description"><b>References:</b><BR>\n'
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    aline = '<A href="{}">{}</A>'.format(line, line)
                    description += aline + "\n"
            description += "</P>\n"
        return description

    def html_short_description(self):
        """
        A limited length short description without embelishments like "references".
        """
        import html
        description = str(self.get("Description"))[:256]
        return html.escape(description)


class ThemeOntology(object):
    def __init__(self, paths=None, imply_collection=False):
        self.theme = {}
        self.story = {}
        self.entries = defaultdict(list)
        self._imply_collection = imply_collection
        if paths:
            if isinstance(paths, (list, tuple)):
                for path in paths:
                    self.read(path)
            else:
                self.read(paths)

    def stories(self):
        """
        Iterate over all story entries defined in no particular order.
        """
        for story in self.story.values():
            yield story

    def themes(self):
        """
        Iterate over all theme entries defined in no particular order.
        """
        for theme in self.theme.values():
            yield theme

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
                collection_entry = None
                for idx, entrylines in enumerate(TOParser.iter_entries(fh)):
                    entry = entrytype(entrylines)
                    entry.ontology = self
                    self.entries[path].append(entry)
                    if isinstance(entry, TOTheme):
                        self.theme[entry.name] = entry
                    elif isinstance(entry, TOStory):
                        self.story[entry.name] = entry
                        if idx == 0:
                            mycols = entry.get("Collections").parts
                            if mycols and mycols[0] == entry.sid:
                                collection_entry = entry
                        if idx > 0 and self._imply_collection and collection_entry:
                            #print("{}  --->  {}".format(entry.sid, collection_entry.sid))
                            field = collection_entry.get("Component Stories")
                            field.parts.append(entry.sid)
                    else:
                        raise

    def validate(self):
        """
        Yields warnings about recognized problems with the data.
        """
        lookup = defaultdict(dict)
        for path, entries in self.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield u"{}: {}".format(path, warning)
                if entry.name in lookup[type(entry)]:
                    yield u"{}: Multiple {} with name '{}'".format(path, type(entry), entry.name)

    def write_clean(self, verbose=False):
        """
        Write the ontology back to its source file while cleaning up syntax and
        omitting unknown field names.
        """
        for path, entries in self.entries.items():
            lines = []
            for entry in entries:
                lines.append(entry.text_canonical())
                lines.append("")
            with codecs.open(path, "w", encoding='utf-8') as fh:
                if verbose:
                    print(path)
                fh.writelines(x + "\n" for x in lines)


def read(paths=None, imply_collection=False):
    if not paths:
        import credentials
        paths = os.path.join(credentials.GIT_THEMING_PATH, "notes")
    return ThemeOntology(paths, imply_collection=imply_collection)

