import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import os
import tempfile
import time
import csv

import webobject
from webphp import php_get

    
def handle_download():
    target = php_get("what")
    klass = {
        "storydefinitions": webobject.Story,
        "themedefinitions": webobject.Theme,
        "storythemes": webobject.StoryTheme,
    }[target]
    
    #: note, above dict lookup guarantees target is safe
    td = tempfile.gettempdir()
    path = os.path.join(td, "%s.csv" % target)
    
    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        timeout = 0
        if mtime + timeout < time.time():
            os.unlink(path)
        else:
            return path
        
    remap = {
        "name": target[:5],
        "name1": "story",
        "name2": "theme",
    }
    
    objs = klass.load()
    headers = [ f for f in klass.fields if "category" not in f ]
    rows = [ [remap.get(f, f) for f in headers] ]
    
    for obj in objs:
        row = []
        for field in headers:
            row.append(unicode(getattr(obj, field)).encode("utf-8"))
        rows.append(row)
        
    with open(path, "wb+") as fh:
        writer = csv.writer(fh, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
        
    return path
    

if __name__ == '__main__':
    try:
        ret = handle_download()
        if isinstance(ret, unicode):
            with open(ret, "r+") as fh:
                print fh.read()
        else:
            print "<pre>", type(ret), ret, "</pre>"
    
    except OSError, e:
        print "<pre>", e, "</pre>"
        
    except:
        raise # TODO remove in prod
        pass


