import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")
import json
from webphp import php_get as get
import cPickle as pickle
import hashlib
import tempfile
import os.path
import time 


def get_data_path(name):
    """
    Get temp path for this data and make sure it exists.
    """
    path = os.path.join(tempfile.gettempdir(), name)
    if not os.path.exists(path):
        os.makedirs(path)    
    return path


def get_data(name, func, parameters = None):
    """
    Fetch a named dataset.
    """
    s = pickle.dumps(parameters)
    m = hashlib.md5()
    m.update(s)

    base_path = get_data_path(name)
    path = os.path.join(base_path, m.hexdigest() + ".pickle")
    data = None

    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        timeout = 3600
        if mtime + timeout < time.time():
            os.unlink(path)
        else:
            with open(path, "rb") as fh:
                data = pickle.load(fh)

    if not data:
        data = func()
        with open(path, "wb") as fh:
            pickle.dump(data, fh, protocol = pickle.HIGHEST_PROTOCOL)

    return data


def handle_query():
    """
    Handle any and all requests for visualization data and 
    return result as json.
    """
    subject = get("subject")
    data = None

    if subject == "viz.themecube":
        from viz.themecube import get_viz_data
        data = get_data(subject, get_viz_data, None)

    if data is not None:
        return json.dumps(data)

    return json.dumps({
        "error" : "unknown request: %s." % str(subject),
    })


if __name__ == '__main__':
    try:
        print handle_query()

    except:
        raise # TODO remove in prod
        pass


