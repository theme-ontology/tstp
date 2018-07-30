import os
import os.path
import webdb
import hashlib
import cPickle as pickle
import log
import tempfile
from db import do
import json
import re
import datetime


TARGET = "web"


def get_data_path(name, *args):
    """
    Get temp path for this data and make sure it exists.
    """
    path = os.path.join(tempfile.gettempdir(), name, *args)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_cache_path(act_type, req_type, obj_name):
    """
    Generate cache path for query.
    """
    key = (act_type,)
    m = hashlib.md5()

    if act_type == "stats" and req_type == "theme":
        key += (obj_name,)

    for part in key:
        m.update(str(part))

    base_path = get_data_path(TARGET + "query")
    path = os.path.join(base_path, m.hexdigest() + ".pickle")

    return path


def cached_special_query(act_type, req_type, obj_name):
    """
    Use cached version if available, else re-generate.
    """
    path = get_cache_path(act_type, req_type, obj_name)

    if os.path.isfile(path):
        log.debug("returning cached: %s", path)
        with open(path, "rb") as fh:
            return pickle.load(fh)
    else:
        log.warn("missing cache: %s", path)

    if act_type == "themelist":
        themes = list( x[0] for x in do("""
            SELECT DISTINCT name from `web_attributes`
            WHERE category = "theme"
        """))
        return json.dumps(themes)

    if act_type == "metathemedata":
        from webdb import get_metatheme_data
        return json.dumps(get_metatheme_data())

    if act_type == "themesimilarity":
        from lib.datastats import get_themes_similarity_v1
        return json.dumps(get_themes_similarity_v1())
        
    if act_type == "stats" and req_type == "theme":
        from lib.datastats import get_theme_stats
        return json.dumps(get_theme_stats(obj_name))

    if act_type in webdb.SUPPORTED_OBJECTS:
        return json.dumps(webdb.get_defenitions(act_type))

    return None


def cache_special_query(act_type, req_type, obj_name):
    path = get_cache_path(act_type, req_type, obj_name)

    if os.path.isfile(path):
        log.debug("deleting for %s, %s: %s", act_type, req_type, path)
        os.unlink(path)

    data = cached_special_query(act_type, req_type, obj_name)
    log.debug("caching for %s, %s: %s", act_type, req_type, path)

    with open(path, "wb") as fh:
        pickle.dump(data, fh, protocol=pickle.HIGHEST_PROTOCOL)

    log.debug("..pickle size: %.2f Mb", os.stat(path).st_size / (1024.0 ** 2))

    if (req_type, obj_name) == (None, None):
        base_path = get_data_path(TARGET + "json")
        path = os.path.join(base_path, act_type + ".json")
        with open(path, "wb+") as fh:
            fh.write(data)

    log.debug("..json size: %.2f Mb", os.stat(path).st_size / (1024.0 ** 2))


def cache_special_queries():
    """
    Generate known special queries and cache them for quick lookup.
    """
    for act_type, req_type, obj_name in list_special_queries():
        cache_special_query(act_type, req_type, obj_name)


def list_special_queries():
    """
    List known special queries (so they may be pre-cached).
    """
    queries = [
        ("themelist", None, None),
        ("metathemedata", None, None),
        ("themesimilarity", None, None),
    ] + [
        (a, None, None) for a in webdb.SUPPORTED_OBJECTS
    ]
    return queries


def get_valid_filename(s):
    """
    Turn string into something that makes a decent filename.
    :param s: string
    :return: better string
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def interpret_daterange(txt):
    """
    Return two datetimes as strings, defaulting to 01-01-01 when
    format is incomplete or faulty.
    """
    dates = [[]]

    for token in txt.split("-"):
        token = token.strip()
        try:
            int(token)
        except ValueError:
            token = '01'
        if (len(token) > 2 and dates[-1]) or len(dates[-1]) == 3:
            dates.append([])
        dates[-1].append(token)

    for date in dates:
        while len(date) < 3:
            date.append('01')
        if not 1 <= int(date[1]) <= 12:
            date[1] = '01'
        for ii in xrange(1, 4):
            try:
                d = datetime.date(*(int(x) for x in date))
            except ValueError:
                d[-ii] = '01'
            else:
                break

    d1, d2 = dates[0], dates[-1]
    return '-'.join(d1), '-'.join(d2)


def cache_objects():
    """
    Save themes and stories as json files.
    """
    for objt in webdb.SUPPORTED_OBJECTS:
        size = 0
        header = []
        base_path = get_data_path(TARGET + "json", objt)
        log.info("writing to: %s", base_path)

        for ii, row in enumerate(webdb.get_defenitions(objt)):
            if "storytheme" in objt:
                continue
            if ii == 0:
                header = row
            else:
                fn = get_valid_filename(row[0].decode("utf-8").encode("ascii", "ignore"))
                path = os.path.join(base_path, fn + ".json")
                data = {k: v for k, v in zip(header, row)}
                data['type'] = objt
                data['_text_'] = '\n\n'.join(row)
                data['id'] = objt + "_" + fn

                if 'date' in data:
                    d1, d2 = interpret_daterange(data['date'])
                    data['date'] = d1
                    data['date2'] = d2

                with open(path, "wb+") as fh:
                    json.dump(data, fh)
                size += os.stat(path).st_size / (1024.0 ** 2)

        log.debug("..total json size: %.2f Mb", size)

