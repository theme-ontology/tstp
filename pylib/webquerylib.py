import os
import os.path
import webdb
import hashlib
import cPickle as pickle
import log
import tempfile
from db import do
import json


def get_data_path(name):
    """
    Get temp path for this data and make sure it exists.
    """
    path = os.path.join(tempfile.gettempdir(), name)
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

    base_path = get_data_path("webquery")
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


def cache_special_queries():
    """
    Generate known special queries and cache them for quick lookup.
    """
    for act_type, req_type, obj_name in list_special_queries():
        path = get_cache_path(act_type, req_type, obj_name)

        if os.path.isfile(path):
            log.debug("deleting for %s, %s: %s", act_type, req_type, path)
            os.unlink(path)

        data = cached_special_query(act_type, req_type, obj_name)
        log.debug("caching for %s, %s: %s", act_type, req_type, path)

        with open(path, "wb") as fh:
            pickle.dump(data, fh, protocol = pickle.HIGHEST_PROTOCOL)

        log.debug("..size: %.2f Mb", os.stat(path).st_size / (1024.0 ** 2))


def list_special_queries():
    """
    List known special queries (so they may b epre-cached).
    """
    queries = [
        ("themelist", None, None),
        ("metathemedata", None, None),
        ("themesimilarity", None, None),
    ] + [
        (a, None, None) for a in webdb.SUPPORTED_OBJECTS
    ]
    return queries



