import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import webobject
import traceback
import cgi
import json
import re
import urllib
from collections import defaultdict

from webphp import php_get as get
import webdb

from webquerylib import (
    cached_special_query,
)


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
    fuzzysearch = get('fuzzysearch', None)
    collapsecollections = get('collapsecollections', None)
    regexpnamefilter = get('regexpnamefilter', None)
    collectionfilter = get('collectionfilter', None)

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

    ## order items according to a search string and "fuzzy" string matching heuristics
    if fuzzysearch is not None:
        from difflib import SequenceMatcher as SM
        import shlex

        extra_fields = ("score",)

        for obj in objs:
            sscore = 0.0
            scount = 0.0
            needles = shlex.split(fuzzysearch.replace("'", "\\'"))

            for needle in needles:
                if needle:
                    needle = needle.replace("\\", "")
                    scores = []
                    haystacks = [ obj.name ] + [ getattr(obj, f) for f in fields if f not in ("name", "score") ]

                    for idx, haystack in enumerate(haystacks):
                        sm = SM(None, haystack, needle)
                        blocks = list(sm.get_matching_blocks())
                        if blocks:
                            score = max(n for i, j, n in blocks) / float(len(needle))
                            score /= 1 + idx / 10.0
                            scores.append(score)
                    if scores:
                        sscore += max(scores)
                        scount += 1

            obj.score = sscore / scount if scount else 0.0
            obj.extra_fields = extra_fields

        objs.sort(key = lambda o: o.score, reverse = False)

    ## show one series entry instead of every episode in a series, etc.
    miscstory = webobject.Story.create(
        name="Collection: Miscellaneous",
        title="Miscellaneous",
        date="various",
        description="Otherwise uncategorized stories in the database."
    )
    everystory = webobject.Story.create(
        name="Collection: All",
        title="All Stories",
        date="various",
        description="All defined stories in the database."
    )
    if collapsecollections == "on" and issubclass(obj_type, webobject.Story):
        colls = set()
        for obj in objs:
            colls.update(x for x in obj.collections.split("\n") if x)
        objs = [o for o in objs if o.name in colls]
        objs.append(miscstory)
        objs.append(everystory)

    # filter by collection name or general regex
    if collectionfilter == miscstory.name:
        objs = [o for o in objs if not o.collections.strip()]
    elif collectionfilter == everystory.name:
        pass
    elif collectionfilter is not None:
        objs = [o for o in objs if collectionfilter in o.collections.split("\n")]

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
    obj_name = get("name")

    log.debug("responding to: %s, %s, %s", act_type, req_type, obj_name)

    res = cached_special_query(act_type, req_type, obj_name)
    if res:
        return res

    ## queries for each object type available
    if obj_type:
        if act_type == "submit":
            handle_submit(obj_type)
        return handle_response(obj_type, req_type)
    
    else:
        return json.dumps({
            "error" : "unknown request: %s." % str((req_type, act_type, obj_type)),
        })


if __name__ == '__main__':
    try:
        print handle_query()

    except:
        raise # TODO remove in prod
        pass


