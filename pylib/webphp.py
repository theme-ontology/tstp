import cgi
import sys
import json


GET = {}
POST = {}
FILES = {}


if len(sys.argv) >= 2:
    with open(sys.argv[1], "r") as fh:
        data = fh.read()
        payload = json.loads(data)
        POST = payload["POST"]
        GET = payload["GET"]
        FILES = payload["FILES"]
        PHP_SESSION_ID = payload["PHP_SESSION_ID"]


if not POST and not GET:
    FORM = cgi.FieldStorage()


class UploadException(Exception):
    pass


def php_get(vname, default=None):
    if POST:
        return POST.get(vname, default)
    if GET:
        return GET.get(vname, default)
    if FORM:
        return FORM.getvalue(vname, default)
    return None


def php_keys():
    if POST:
        return POST.keys()
    if GET:
        return GET.keys()
    if FORM:
        return FORM.keys()
    return []


