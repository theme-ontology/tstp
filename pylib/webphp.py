import cgi
import sys
import json
import hashlib
import os
import os.path
import tempfile


GET = {}
POST = {}
FILES = {}


try:
    if len(sys.argv) >= 2:
        with open(sys.argv[1], "r") as fh:
            data = fh.read()
            payload = json.loads(data)
            POST = payload["POST"]
            GET = payload["GET"]
            FILES = payload["FILES"]
            PHP_SESSION_ID = payload["PHP_SESSION_ID"]
except IOError:
    pass


if not POST and not GET:
    FORM = cgi.FieldStorage()


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


def get_userfile_path(name):
    m = hashlib.md5()
    m.update(str(PHP_SESSION_ID))
    path = os.path.join(tempfile.gettempdir(), m.hexdigest()[:10])

    if not os.path.exists(path):
        os.makedirs(path)    

    return os.path.join(path, name)


def get_pending_path():
    return os.path.join(tempfile.gettempdir(), "batch_events_%s" % PHP_SESSION_ID)



