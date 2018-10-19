import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
log.set_templog("web.log")

import json
from webphp import php_get as get
from lib.files import safe_filename
from credentials import GIT_THEMING_PATH
import os.path
import os
import subprocess



def handle_query():
    """
    Handle any and all web submits.
    """
    action = get("action")
    log.debug("responding to: %s", action)

    ## queries for each object type available
    if action == "protostory":
        data = (get("storyentry") or "").strip()
        rows = data.split("\n")
        sid = None
        path = None
        results = []
        retval = {}

        for idx, row in enumerate(rows):
            if row.startswith("===") and idx > 0:
                sid = rows[idx-1].strip()
                break

        if sid:
            fn = safe_filename(sid) + ".st.txt"
            basepath = os.path.join(GIT_THEMING_PATH, "auto", "pending")
            if not os.path.exists(basepath):
                os.makedirs(basepath)
            os.chdir(basepath)
            results.append(subprocess.check_output("git pull".split(), stderr=subprocess.STDOUT))
            if not os.path.exists(basepath):
                os.makedirs(basepath)
            path = os.path.join(basepath, fn)
            overwrite = os.path.isfile(path)
            with open(path, "wb+") as fh:
                fh.write(data)
                fh.write("\n")
            cmd = [ 'git', 'add', fn ]
            results.append(subprocess.check_output(cmd, stderr=subprocess.STDOUT))
            cmd = [ 'git', 'commit', '-m', "auto: prototype storyentry from web: %s" % fn ]
            results.append(subprocess.check_output(cmd, stderr=subprocess.STDOUT))
            results.append(subprocess.check_output("git push".split(), stderr=subprocess.STDOUT))
        else:
            retval.update({
                "error": "Commit failed.",
            })

        retval.update({
            "stdout": "\n".join(results),
            "overwrite": overwrite,
            "filename": path,
        })
        return json.dumps(retval)

    else:
        return json.dumps({
            "error" : "unknown request: %s." % str(action),
        })


if __name__ == '__main__':
    try:
        print handle_query()
    except:
        raise # TODO remove in prod
        pass


