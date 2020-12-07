# Copyright 2020, themeontology.org
# Tests:
import lib.log
import os


def run_task(taskname):
    """
    pyrun webtask.taskname
    """
    cmd = "pyrun webtask.%s" % taskname
    lib.log.info("executing: %s", cmd)
    code = os.system(cmd)
    lib.log.info("command finished with code %s", code)
    return code

