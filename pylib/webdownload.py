import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import os
import os.path
import tempfile
import time
import csv
import codecs

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
    out_fmt = webphp.php_get("fmt", "csv")

    #: an already  prepared file for user?
    if target.startswith("user") and target.isalnum():
        path = webphp.get_userfile_path(target) + ".xls"
        assert os.path.isfile(path)
        return path, True, out_fmt

    #: list objects of given types?
    #: note, important for security
    assert target in webdb.SUPPORTED_OBJECTS
    assert out_fmt in [ "csv", "xls", "txt" ]

    td = tempfile.gettempdir()
    path = os.path.join(td, "%s.%s" % (target, out_fmt))
    
    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        timeout = 60
        if mtime + timeout < time.time():
            os.unlink(path)
        else:
            return path, False, out_fmt
        
    if out_fmt == "txt":
        blob = webdb.get_defenitions_text(target)
        with open(path, "wb+") as fh:
            fh.write(blob.encode("utf-8"))
        return path, False, out_fmt

    elif out_fmt in ("csv", "xls"):
        rows = webdb.get_defenitions(target)
        with open(path, "wb+") as fh:
            writer = csv.writer(fh, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(rows)
        return path, False, out_fmt


def handle():

    try:
        ret, binary, out_fmt = handle_download()
        fmt = "rb" if binary else "r"
        log.debug("Download prepared: %s, (%s%s)", ret, out_fmt, " <binary>" if binary else " <plain>")

        if binary:
            print ret

        elif isinstance(ret, unicode):
            with codecs.open(ret, fmt, encoding="utf-8") as fh:
                print fh.read()
        else:
            print "<pre>", type(ret), ret, "</pre>"
    
    except OSError, e:
        print "<pre>", e, "</pre>"
        
    except:
        raise # TODO remove in prod
        pass


if __name__ == '__main__':
    handle()