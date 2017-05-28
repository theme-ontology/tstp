import cgitb; cgitb.enable()
import log; log.set_level('SILENT')
log.set_logfile("web.log")

import webobject
import traceback
import cgi
import os
import json
from pprint import pprint as pp
import sys
from db import do
from collections import defaultdict
import excel
import tempfile
import cPickle as pickle

from webobject import StoryTheme, Story, Theme
from webphp import php_get, FILES, PHP_SESSION_ID


class UploadException(Exception):
    pass


def get_pending_path():
    return os.path.join(tempfile.gettempdir(), "batch_events_%s" % PHP_SESSION_ID)


def cancel_pending_events():
    fn = get_pending_path()
    try:
        os.unlink(fn)
    except (IOError, OSError):
        pass
    

def get_pending_events():
    fn = get_pending_path()
    try:
        with open(fn, "rb") as fh:
            return pickle.load(fh)["events"]
    except (IOError, KeyError):
        return []
    
    
def save_pending_events(events):
    fn = get_pending_path()
    with open(fn, "wb+") as fh:
        pickle.dump({ "events": events }, fh, 1)
    

def read_xls(filename, headers):
    """
    Return cells in rows with given headers for all sheets in file.
    """
    sheetcount = 0
    rowcount = 0
    
    try:
        sheets = excel.xls_sheet_to_memory(filename)
    except (OSError, KeyError):
        raise UploadException("Unable to read excel file")
    
    results = []
    idxs = []
    
    for sheet in sheets:
        sheetcount += 1
        for idx, row in enumerate(sheets[sheet]):
            if idx == 0:
                idxs = []
                for header in headers:
                    try:
                        idxs.append(row.index(header))
                    except ValueError:
                        raise UploadException("Missing header: '%s' in %s" % (header, str(row)))
                continue
            
            rowcount += 1
            results.append([ row[i] for i in idxs ])
    
    return results, sheetcount, rowcount

    
def read_storythemes(filename):
    weights = {
        "Choice Theme": "choice",
        "Major Theme": "major",
        "Minor Theme": "minor",
        "Absent Theme": "absent",
    }
    headers = [
        "StoryID", 
        "Keyword", 
        "FieldName", 
        "Comment",
    ]
    relations, sheetcount, rowcount = read_xls(filename, headers)
    
    sids = sorted(set(x[0].lower() for x in relations))
    themes = sorted(set(x[1] for x in relations))
    existing = StoryTheme.load(name1s = sids)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[(st.name1, st.name2)] = st
        
    for sid, kw, fieldname, motivation in relations:
        try:
            weight = weights[fieldname]
        except KeyError:
            if weight not in weights.values():
                raise UploadException("Unexpected FieldName: %s" % fieldname)
        
        sid = sid.lower()
        st = exist_lu.get((sid, kw), None)
        
        if st is None:
            # add insert event
            st = StoryTheme.create(sid, kw, weight, motivation)
            events.extend(st.make_insert_events())
        else:
            if st.weight != weight:
                # edit field/weight
                events.append(st.make_edit_event("weight", weight))
            if st.motivation != motivation:
                # edit motivation
                events.append(st.make_edit_event("motivation", motivation))

    return events, sheetcount, rowcount


def read_stories(filename):
    headers = [
        "StoryID", 
        "Title", 
        "ReleaseDate", 
        "Description",
    ]
    stories, sheetcount, rowcount = read_xls(filename, headers)
    
    sids = sorted(set(x[0].lower() for x in stories))
    existing = Story.load(names = sids)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[st.name] = st
        
    for sid, title, releasedate, description in stories:
        sid = sid.lower()
        st_old = exist_lu.get(sid, None)
        st_new = Story.create(
            name = sid,
            title = title,
            date = releasedate,
            description = description,
        )
        events.extend(st_new.make_edit_events(st_old))

    return events, sheetcount, rowcount


def read_themes(filename):
    headers = [
        "Keyword", 
        "Implications", 
        "Definition", 
    ]
    stories, sheetcount, rowcount = read_xls(filename, headers)
    
    keywords = sorted(set(x[0] for x in stories))
    existing = Theme.load(names = keywords)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[st.name] = st
        
    for keyword, parents, description in stories:
        st_old = exist_lu.get(keyword, None)
        st_new = Theme.create(
            name = keyword,
            description = description,
            parents = parents,
        )
        events.extend(st_new.make_edit_events(st_old))

    return events, sheetcount, rowcount

    
def handle_upload():
    submit = php_get("submit")
    
    if submit == "cancel":
        cancel_pending_events()
      
    elif submit == "commit":
        cancel_pending_events()
    
    elif submit == "submitfile":
        ftype = php_get("fieldType")
        meta = FILES["fieldFile"]
        filename = meta["tmp_name"]
        name = meta["name"]
        events = None
        
        if ftype == "storythemes":
            events, sheetcount, rowcount = read_storythemes(filename)
        elif ftype == "storydefinitions":
            events, sheetcount, rowcount = read_stories(filename)
        elif ftype == "themedefinitions":
            events, sheetcount, rowcount = read_themes(filename)
        else:
            return "Type %s is not yet supported" % ftype 
        
        if events is not None:
            save_pending_events(events)
            message = "" if events else "Nothing to do."
            message += " Found %s changes in %s sheets and %s rows." % (
                len(events),
                sheetcount,
                rowcount,
            )
            return message


if __name__ == '__main__':
    try:
        result = handle_upload()
        if isinstance(result, str):
            print result
    
    except UploadException, e:
        print "<pre>", e, "</pre>"
        
    except:
        raise # TODO remove in prod
        pass


