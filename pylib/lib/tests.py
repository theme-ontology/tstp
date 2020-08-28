"""
Name:           tests.py
Description:    Helper functions for running TSTP tests.
"""
import log
import traceback


def run_data_tests(testobj):
    """
    Run test methods in a controlled environment and take not of problems.
    Args:
        testobj: Any method named starting with "test_" will be called.
    Returns:
        Returns a proposed exit code, i.e., 0 if there are no serious problems and
        nonzero otherwise.
    """
    exitcode = 0
    failedcount = 0
    successcount = 0

    for name in dir(testobj):
        if name.startswith("test_"):
            meth = getattr(testobj, name)
            res = None
            log.debug("RUNNING %s..." % name)
            try:
                res = meth()
            except:
                log.debug("ERROR in %s!" % name)
                exitcode = max(exitcode, 2)
                res = "test raised exception"
                traceback.print_exc()
            if res:
                log.debug("FAIL in %s!" % name)
                exitcode = max(exitcode, 1)
                failedcount += 1
                log.debug(res)
            else:
                log.debug("SUCCESS")
                successcount += 1

    log.debug("DONE Running tests. %d Failed, %d Succeeded." % (failedcount, successcount))
    return exitcode


