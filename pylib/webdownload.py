import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import os
import os.path
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

    #: an already  prepared file for user?
    if target.startswith("user") and target.isalnum():
        path = webphp.get_userfile_path(target) + ".xls"
        assert os.path.isfile(path)
        return path, True

    #: list objects of given types?
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
            return path, False
        
    rows = webdb.get_defenitions(target)
        
    with open(path, "wb+") as fh:
        writer = csv.writer(fh, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
        
    return path, False
    

if __name__ == '__main__':
    try:
        ret, binary = handle_download()
        fmt = "rb" if binary else "r"

        if binary:
            print ret

        elif isinstance(ret, unicode):
            with open(ret, fmt) as fh:
                print fh.read()
        else:
            print "<pre>", type(ret), ret, "</pre>"
    
    except OSError, e:
        print "<pre>", e, "</pre>"
        
    except:
        raise # TODO remove in prod
        pass


