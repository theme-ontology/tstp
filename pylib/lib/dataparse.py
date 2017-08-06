import re

import webobject
import lib.xls
import lib.log


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


SUBJECTS = {
    "Ratings": lambda lines: [ t.strip() for t in line.split(", ") for line in lines ],
    "Choice Themes": parse_themes,
    "Major Themes": parse_themes,
    "Minor Themes": parse_themes,
}


def parse(file):
    """
    Parse a file of themes and related info.
    """
    sections = []
    lines = []
    notices = []
    stuff = []

    # sections are delimeted by identifier underlined with ===
    with open(file, "r") as fh:
        for line in fh.readlines():
            if line.startswith("==="):
                sections.append(lines)
                lines = [ lines.pop() ]
            lines.append(line.strip())
    sections.append(lines)

    # subjects begin with "::", content may be parsed in different ways
    for lines in sections:
        identifier = lines[0]
        subject = None
        lineacc = []

        for idx, line in enumerate(lines):
            # hack to handle EOF
            if idx == len(lines) - 1:
                lineacc.append(line)
                line = ":: "

            # parse previous subject when subject changes
            if line.startswith(":: "):
                if subject:
                    if subject in SUBJECTS:
                        parser = SUBJECTS[subject]
                    else:
                        parser = lambda lines: [ " ".join(line.strip() for line in lines).strip() ]

                    try:
                        stuff.append((identifier, subject, list(parser(lineacc))))
                    except Exception:
                        notices.append('Failed to parse data for "%s" in "%s"' % (subject, identifier))

                subject = line[3:].strip()
                lineacc = []

            # accumulate lines of subject
            else:
                lineacc.append(line)

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


def read_themes_from_txt(filename):
    """
    Themes in our special text file format.
    """
    themestuff, notices = parse(filename)
    out_themes = {}
    field_map = {
        "description": "description",
        "parents": "parents",
    }

    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)

    for theme, field, data in themestuff:
        if theme not in out_themes:
            out_themes[theme] = webobject.Theme(
                name = theme,
            )

        themeobj = out_themes[theme]
        attr = field_map.get(field.lower(), None)

        if attr and attr in themeobj.fields:
            setattr(themeobj, attr, data[0])
        else:
            lib.log.warn("%s: %s.%s - don't grok", filename, theme, field)

    for key in sorted(out_themes):
        themeobj = out_themes[key]
        themeobj.test_fields()
        yield themeobj


def read_stories_from_txt(filename):
    """
    Stories in our special text file format.
    """
    stuff, notices = parse(filename)
    out = {}
    field_map = {
        "title": "title",
        "release date": "date",
        "description": "description",
    }

    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)

    for item, field, data in stuff:
        if item not in out:
            out[item] = webobject.Story(
                name = item,
            )

        obj = out[item]
        attr = field_map.get(field.lower(), None)

        if attr and attr in obj.fields:
            setattr(obj, attr, data[0])
        else:
            lib.log.warn("%s: %s.%s - don't grok", filename, item, field)

    for key in sorted(out):
        obj = out[key]
        obj.test_fields()
        yield obj


def read_storythemes_from_txt(filename):
    """
    Themes-in-stories in our special text file format.
    """
    stuff, notices = parse(filename)
    out = {}

    for notice in notices:
        lib.log.warn("%s: %s", filename, notice)

    for sid, field, data in stuff:
        if field.lower().endswith("themes"):
            weight = field.split(" ")[0].lower()
            assert weight in ("absent", "minor", "major", "choice")

            for theme, motivation in data:
                yield webobject.StoryTheme.create(
                    sid, theme, weight, motivation
                )


def read_themes_from_xls(filename):
    """
    Themes in our spreadsheet format.
    """
    headers = [
        "Keyword", 
        "Implications", 
        "Definition", 
    ]
    stuff, sheetcount, rowcount = lib.xls.read_xls(filename, headers)
        
    for keyword, parents, description in sorted(stuff):
        yield webobject.Theme.create(
            name = keyword,
            description = description,
            parents = parents,
        )        


def read_stories_from_xls(filename):
    """
    Stories in our spreadsheet format.
    """
    headers = [
        "StoryID", 
        "Title", 
        "ReleaseDate",
        "Description",
    ]
    stuff, sheetcount, rowcount = lib.xls.read_xls(filename, headers)
        
    for sid, title, rdate, description in sorted(stuff):
        yield webobject.Story.create(
            name = sid,
            title = title,
            date = rdate,
            description = description,
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


