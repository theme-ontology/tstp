import cgitb; cgitb.enable()
import log; log.set_level('SILENT')
log.set_logfile("web.log")

import webobject
import traceback
import cgi
import os
import json
import pprint
import sys
from db import do

from webphp import php_get as get



OBJECT_TYPES = {
    "story": webobject.Story,
    "theme": webobject.Theme,
    "storytheme": webobject.StoryTheme,
    "event": webobject.TSTPEvent,
    "proposedevents": webobject.TSTPEvent,
}


def handle_submit(obj_type):
    """
    Do the db-update part of the query.
    """
    if issubclass(obj_type, webobject.TSTPConnection):
        update = get("data")
        attrs = [ x[0] for x in update ]
        vals = [ x[1] for x in update ]
        cat1 = get("type1")
        name1 = get("filter1")
        cat2 = get("type2")
        name2 = get("filter2")
        obj_type.edit_object(cat1, name1, cat2, name2, attrs, vals)

    else:
        update = get("data")
        attrs = [ x[0] for x in update ]
        vals = [ x[1] for x in update ]
        cat = get("type")
        name = get("filter")
        obj_type.edit_object(cat, name, attrs, vals)


def handle_response(obj_type, variant = None):
    """
    Do the JSON response part of the query.
    """
    string_limit = int(get('slimit', 100))
    row_limit = int(get('rlimit', 10000))
    fields = (get('fields') or '').split(',')
    
    if variant == "proposedevents":
        # a list of events session user has proposed for insertion,
        # not yet stored in database
        from webupload import get_pending_events
        objs = get_pending_events()

    elif issubclass(obj_type, webobject.TSTPEvent):
        cat1s = get('c1')
        name1s = get('f1')
        cat2s = get('c2')
        name2s = get('f2')
        objs = obj_type.load(
            cat1s = cat1s,
            name1s = name1s,
            cat2s = cat2s,
            name2s = name2s,
            limit = row_limit,
        )

    elif issubclass(obj_type, webobject.TSTPConnection):
        name1s = get('f1')
        name2s = get('f2')
        objs = obj_type.load(
            name1s = name1s, 
            name2s = name2s, 
            limit = row_limit,
        )

    else:
        names = get('filter')
        objs = obj_type.load(
            names = names, 
            limit = row_limit,
        )

    return obj_type.make_json(
        objs, 
        fields = fields, 
        limit = string_limit,
    )


def handle_query():
    """
    Handle any and all web queries and return result as json.
    
    POST Parameters
    ---------------
    action:
        "submit" if edits are to be carried out, or the name
        of a special query type.
    type:
        E.g. "story", "theme", "storytheme", etc. indicating what kind of
        object is concerned. 
    """
    act_type = get("action")
    req_type = get("type")
    obj_type = OBJECT_TYPES.get(req_type)

    ## special queries
    if act_type == "themelist":
        themes = list( x[0] for x in do("""
            SELECT DISTINCT name from `web_attributes`
            WHERE category = "theme"
        """))
        return json.dumps(themes)

    ## queries for each object type available
    if obj_type:
        if act_type == "submit":
            handle_submit(obj_type)

        return handle_response(obj_type, req_type)
    
    else:
        return json.dumps({
            "error" : "unknown request: %s." % str((req_type, act_type, obj_type)),
            "post" : POST,
        })


if __name__ == '__main__':
    try:
        print handle_query()

    except:
        raise # TODO remove in prod
        pass


