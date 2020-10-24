import re
import codecs
from collections import defaultdict
import json

import webobject
import lib.xls
import lib.log
import textwrap
from lib.func import memoize
import lib.textformat


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
    if isinstance(txt, basestring):
        field = txt
    else:
        field = " ".join(x.strip() for x in txt)

    for kw, comment, _implication, _capacity in expload_field(field):
        yield kw, comment


def simple_line_collection(lines):
    return [ t.strip() for line in lines for t in line.split(", ") ]


def sanitize(lines):
    """
    Strip whitespace around each lines and remove blank lines at beginning
    and end of blob (but not in between text).
    """
    i = 0
    lines = [ x.strip() for x in lines ]
    while lines and not lines[-1]:
        lines.pop()
    for i, l in enumerate(lines):
        if l:
            break
    if i > 0:
        lines = lines[i:]
    if not lines:
        lines = [""]
    return lines


def make_themes(fieldinfo, empty_comments=True):
    """
    Take a list of tuples as yielded by expload_field and format into themes block.
    """
    outlines = []
    for kw, comment, implication, capacity in fieldinfo:
        implication = implication.strip()
        capacity = capacity.strip()
        comment = comment.strip()
        if comment or empty_comments:
            f = kw.strip() + " [%s]" % comment.strip()
        else:
            f = kw.strip()
        if implication:
            f += " {%s}" % implication
        if capacity:
            f += " <%s>" % capacity
        outlines.append(f)

    if not outlines:
        return ""
    return ",\n".join(outlines) + ","


def themejoin(lines, empty_comments=True):
    """
    Format lines of theme specification into a standard format.
    """
    if isinstance(lines, basestring):
        field = lines
    else:
        field = " ".join(x.strip() for x in lines).strip(' ,')
    fielditer = expload_field(field)
    return make_themes(fielditer, empty_comments=empty_comments)


def block_fill(lines):
    """
    Wordwrap text in paragraphs.
    """
    return lib.textformat.add_wordwrap("\n".join(lines))


def blockjoin(lines):
    """
    Remove breaklines in paragraphs but not between.
    """
    return lib.textformat.remove_wordwrap("\n".join(lines))


def simple_blockfill(lines):
    return [ block_fill(lines) ]


def simple_themejoin(lines):
    return [ themejoin(lines) ]


def simple_keywordjoin(lines):
    return [ themejoin(lines) ]


def simple_fieldclean(lines):
    return ['\n'.join(a for a in [x.strip() for x in lines] if a)]


SUBJECTS_PARSE_THEMES = {
    "Ratings": simple_line_collection,
    "Choice Themes": parse_themes,
    "Major Themes": parse_themes,
    "Minor Themes": parse_themes,
    "References": simple_line_collection,
    "Collections": simple_line_collection,
    "Component Stories": simple_fieldclean,
}


SUBJECTS = {
    "Ratings": simple_line_collection,
    "Choice Themes": simple_themejoin,
    "Major Themes": simple_themejoin,
    "Minor Themes": simple_themejoin,
    "Other Keywords": simple_themejoin,
    "References": simple_line_collection,
    "Collections": simple_line_collection,
    "Component Stories": simple_fieldclean,
    "Description": simple_blockfill,
    "Examples": simple_blockfill,
    "Notes": simple_blockfill,
}


def parse_section_gen(linegen):
    """
    Takes a generator of lines (such a file handle) and yields lists of lines, grouped into
    logical blocks.
    """
    lines = []
    for line in linegen:
        if line.startswith("===") and len(lines) > 1:
            yield lines[:-1]
            lines = [lines.pop()]
        lines.append(line.strip())
    yield lines


def parse_section(section, subjects=None, default_parser=None):
    """
    Take a list of lines that constitute a single section in TO format
    (first line is objects name underlined with "===", then follows "fields"
    like ":: Field Name") and output structured information.
    """
    # subjects begin with "::", content may be parsed in different ways
    identifier = section[0] if section else None
    subject = None
    lineacc = []
    notices = []
    stuff = []

    for idx, line in enumerate(section):
        # hack to handle EOF
        if idx == len(section) - 1:
            lineacc.append(line)
            line = ":: "

        # parse previous subject when subject changes
        if line.startswith(":: "):
            if subject:
                parser = subjects.get(subject, default_parser)
                try:
                    stuff.append((identifier, subject, list(parser(lineacc))))
                except Exception:
                    notices.append('Failed to parse data for "%s" in "%s"' % (subject, identifier))
                    raise  # vestigial: we no longer tolerate any errors here
            subject = line[3:].strip()
            lineacc = []

        # accumulate lines of subject
        else:
            lineacc.append(line)

    return stuff, notices


def iter_parse(file, subjects=None, default_parser=None):
    """
    Parse a file of themes and related info.
    Returns:
        yields (stuff, notices) for each object defined
        stuff: list of tuples like (object name, field name, data). object name will be constant in each list.
        notices: (deprecated) list of parse errors, if any.
    """
    if subjects is None:
        subjects = SUBJECTS
    if default_parser is None:
        default_parser = lambda lines: [blockjoin(lines)]
    if default_parser == 'NOOP':
        default_parser = lambda lines: lines
    with codecs.open(file, "r", encoding='utf-8') as fh:
        for section in parse_section_gen(fh):
            stuff, notices = parse_section(section, subjects=subjects, default_parser=default_parser)
            yield (section, stuff, notices)


def parse(file, subjects=None, default_parser=None):
    """
    Parse a file of themes and related info.
    """
    notices = []
    stuff = []
    for _section, ss, nn in iter_parse(file, subjects=subjects, default_parser=default_parser):
        stuff.extend(ss)
        notices.extend(nn)
    return stuff, notices


def read_themes_from_db(limit = 1000000):
    """
    Themes in our db.
    """
    for obj in webobject.Theme.load(limit = limit): 
        yield obj   


def read_stories_from_db(limit = 1000000):
    """
    Stories in our db.
    """
    for obj in webobject.Story.load(limit = limit): 
        yield obj   


def read_storythemes_from_db(limit = 1000000):
    """
    Stories in our db.
    """
    for obj in webobject.StoryTheme.load(limit = limit): 
        yield obj   


def read_themes_from_txt(filename, verbose=True, addextras=False, combinedescription=True, strict=True):
    """
    Themes in our special text file format.
    """
    themestuff, notices = parse(filename)
    out_themes = {}
    out_composites = defaultdict(lambda: defaultdict(str))
    field_map = {
        "parents": "parents",
        "description": "description",
    }
    composite_fields = {
        "description": "description",
        "examples": "examples",
        "notes": "notes",
        "references": "references",
        "aliases": "aliases",
    }
    unused_fieldnames = {
        "related themes",
        "other parents",
    }
    meta = {
        "source": filename,
    }

    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)

    for theme, field, data in themestuff:
        if theme not in out_themes:
            out_themes[theme] = webobject.Theme(name=theme, meta=json.dumps(meta))

        themeobj = out_themes[theme]
        lfield = field.strip().lower()
        attr = field_map.get(lfield, "")

        if lfield in composite_fields:
            out_composites[theme][lfield] = '\n'.join(data)

        if attr in themeobj.fields:
            setattr(themeobj, attr, data[0])
        elif addextras:
            exattr = lfield.replace(" ", "")
            setattr(themeobj, exattr, '\n'.join(data))
            themeobj.extra_fields += (exattr,)
        else:
            if verbose:
                if lfield not in composite_fields and lfield not in unused_fieldnames:
                    lib.log.warn("""%s: "%s": unrecognized field name "%s" """, filename, theme, field)

    for key in sorted(out_themes):
        themeobj = out_themes[key]

        if combinedescription:
            description = getattr(themeobj, "description")
            examples = out_composites[key]["examples"].strip()
            aliases = out_composites[key]["aliases"].strip()
            notes = out_composites[key]["notes"].strip()
            references = out_composites[key]["references"].strip()
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
            themeobj.description = description

        try:
            if strict:
                themeobj.test_fields()
            yield themeobj
        except ValueError as e:
            if verbose:
                lib.log.warn("%s: %s.%s - %s", filename, theme, field, str(e))


def iter_stories_from_txt(filename):
    """
    Iterate over stories in a file, turn them into storyu objects but also
    stamp each object with the blob of verbatim lines specifying it in
    the text file.
    """
    for section, stuff, _notices in iter_parse(filename):
        for obj in read_stories_from_fieldcollection(stuff):
            obj.blob = "\n".join(section)
            yield obj


def read_stories_from_txt(filename, verbose=True, addextras=False, strict=True):
    """
    Stories in special TO text file format as handled by "parse".
    """
    stuff, notices = parse(filename)
    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)
    meta = {"source": filename}
    globcollection = not filename.endswith("-collections.st.txt")
    for obj in read_stories_from_fieldcollection(stuff,
        verbose=(verbose and filename), addextras=addextras, globcollection=globcollection, strict=strict
    ):
        obj.meta.update(meta)
        obj.meta = json.dumps(obj.meta)
        yield obj


def read_stories_from_fieldcollection(fieldcollection, verbose=True, addextras=False, globcollection=False, strict=True):
    """
    Stories in our special text file format.
    """
    out = {}
    out_composites = defaultdict(lambda: defaultdict(str))
    field_map = {
        "title": "title",
        "release date": "date",
        "description": "description",
        "date": "date",
        "collections": "collections",
        "component stories": "components",
    }
    composite_fields = {
        "description": "description",
        "references": "references",
        "collections": "collections",
    }
    recognized_fields = set([
        "authors",
        "choice themes",
        "genre",
        "major themes",
        "minor themes",
        "not themes",
        "notes",
        "other keywords",
        "ratings",
        "related stories",
        "aliases",
    ] + list(composite_fields) + list(field_map))
    global_collections = []

    for sid, field, data in fieldcollection:
        # is this is a "collection" for all stories in this file?
        if globcollection:
            if field.lower() == "collections" and sid in data:
                for d in data:
                    if d not in global_collections:
                        global_collections.append(d)

        if sid not in out:
            out[sid] = webobject.Story(name=sid, meta={})

        obj = out[sid]
        lfield = field.strip().lower()
        attr = field_map.get(lfield, "")

        if lfield in composite_fields:
            out_composites[sid][lfield] = '\n'.join(data)
        if attr and attr in obj.fields:
            setattr(obj, attr, data[0])
        elif addextras:
            exattr = lfield.replace(" ", "")
            setattr(obj, exattr, '\n'.join(data))
            obj.extra_fields += (exattr,)
        elif lfield == "ratings":
            numbers = [int(s) for s in re.findall("\d+", ' '.join(data), re.DOTALL)]
            numbers = [min(5, max(0, n)) for n in numbers]
            count = float(len(numbers))
            if count > 0:
                mean = sum(numbers) / count
                stddev = (sum((x - mean)**2 for x in numbers) / count)**0.5
                obj.meta['rating'] = u'%.2f \u00B1 %.2f' % (mean, stddev)
            else:
                obj.meta['rating'] = 'n/a'
        elif lfield in recognized_fields:
            # recognized so don't warn even if we're not adding them
            pass
        else:
            if verbose:
                lib.log.warn("%s: %s.%s - don't grok", verbose, sid, field)

    for sid in sorted(out):
        obj = out[sid]
        description = getattr(obj, "description", "")
        references = out_composites[sid]["references"].strip()
        collections = out_composites[sid]["collections"].strip()

        if references:
            description += "\n\nReferences:\n"
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    description += line + "\n"

        clist = list(global_collections)
        for c in collections.split("\n"):
            if c and c not in clist:
                clist.append(c)
        clist = [c.strip() for c in clist if c.strip()]

        obj.description = description
        obj.collections = "\n".join(clist)

        try:
            if strict:
                obj.test_fields()
            yield obj
        except ValueError as e:
            if verbose:
                lib.log.warn("%s: %s.%s - %s", verbose, sid, field, str(e))


def read_storythemes_from_txt(filename, verbose = True):
    """
    Themes-in-stories in our special text file format.
    """
    stuff, notices = parse(filename, subjects=SUBJECTS_PARSE_THEMES)
    out = {}

    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)

    for sid, field, data in stuff:
        #data = list(parse_themes(data))
        if field.lower().endswith("themes"):
            weight = field.split(" ")[0].lower()
            if weight in ("absent", "minor", "major", "choice"):
                for theme, motivation in data:
                    yield webobject.StoryTheme.create(
                        sid, theme, weight, motivation
                    )


def read_storythemes_from_xls_compact(filename):
    """
    Story-themes in our compact spreadsheet format.
    """
    headers = [
        "StoryID", 
        "Choice Theme", 
        "Major Theme",
        "Minor Theme",
    ]
    stuff, sheetcount, rowcount = lib.xls.read_xls(filename, headers)
        
    for sid, t1, t2, t3 in sorted(stuff):
        for weight, data in [("choice", t1), ("major", t2), ("minor", t3)]:
            try:
                entries = list(parse_themes(data))
            except (Exception, AssertionError):
                lib.log.error("FAILED in %s, %s: %s.", sid, weight, data)
                raise

            for theme, motivation in entries:
                yield webobject.StoryTheme.create(
                    sid, theme, weight, motivation
                )        


@memoize
def dataframe(source="txt", debug=False):
    """
    Return one big pandas dataframe with all story and theme data in DB.
    Returns:

    """
    import pandas as pd
    import os.path
    import lib.files

    objs = [[], [], []]
    dfs = []

    if source == "txt":
        from credentials import GIT_THEMING_PATH
        basepath = GIT_THEMING_PATH
        notespath = os.path.join(basepath, "notes")
        for path in lib.files.walk(notespath, ".*\.(st|th)\.txt$"):
            if debug:
                print(path)
            if path.endswith(".th.txt"):
                ol = list(lib.dataparse.read_themes_from_txt(path, False))
                objs[0].extend(ol)
            if path.endswith(".st.txt"):
                ol1 = lib.dataparse.read_storythemes_from_txt(path, False)
                ol2 = list(lib.dataparse.read_stories_from_txt(path, False))
                objs[1].extend(ol1)
                objs[2].extend(ol2)
    if source == "db":
        objs[0].extend(read_themes_from_db())
        objs[1].extend(read_storythemes_from_db())
        objs[2].extend(read_stories_from_db())

    for olist in objs:
        fields = olist[0].fields
        for obj in olist:
            if fields != obj.fields:
                raise RuntimeError("Expected all %s objects to have same field definition" % type(obj))
        fields = [f for f in fields if not f.startswith("category") and not f=="meta"]
        data = [[getattr(obj, f) for f in fields] for obj in olist]
        dfs.append(pd.DataFrame(columns=fields, data=data))

    dfT, dfST, dfS = dfs
    dfT.rename(columns={"name": "theme", "description": "theme_def"}, inplace=True)
    dfST.rename(columns={"name1": "sid", "name2": "theme"}, inplace=True)
    dfS.rename(columns={"name": "sid", "description": "story_def"}, inplace=True)
    dfT.set_index("theme", inplace=True)
    dfST.set_index(["sid", "theme"], inplace=True)
    dfS.set_index("sid", inplace=True)

    df = dfST.join(dfS, on="sid", how="left")
    df = df.join(dfT, on="theme", how="left")
    return df


def main():
    df = dataframe()
    dff = df.reset_index()  # because fuck pandas
    dfp = dff[dff["theme"] == "pride"]
    print(dfp)
    df.to_excel("unpurge.xls")
    dfp.to_excel("unpurge_pride.xls")





