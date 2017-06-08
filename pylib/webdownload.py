import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import os
import tempfile
import time
import csv

import webphp
import webdb
    

def handle_download():
    """
    Read GET parameter "what" and produca the appropriate
    cvs file. May be cached.

    Returns
    -------
    Path of csv file.
    """
    target = webphp.php_get("what")

    #: note, important for security
    assert target in webdb.SUPPORTED_OBJECTS

    td = tempfile.gettempdir()
    path = os.path.join(td, "%s.csv" % target)
    
    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        timeout = 60
        if mtime + timeout < time.time():
            os.unlink(path)
        else:
            return path
        
    rows = webdb.get_defenitions(target)
        
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


