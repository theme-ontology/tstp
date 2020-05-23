import sys
import os.path
import lib.files
import subprocess
import lib.log


def runone(cmd):
    """
    Run a test.
    Args:
        mod: valid python module as string
    Returns: (code, stdout, stderr)
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


def alltests():
    """
    Returns: Python modules as that are tests, as strings.
    """
    mod = sys.modules[__name__]
    base = os.path.split(mod.__file__)[0]
    nstem = len(lib.files.split(base)) - 1
    for path in lib.files.walk(base, "test_.*\\.py$"):
        parts = lib.files.split(path)
        mod = '.'.join(parts[nstem:-1] + [parts[-1][:-3]])
        yield mod


def runall():
    """
    Run all tests defined in repository.
    Returns: True if all tests passed successfully. Else False.
    """
    results = {}
    for mod in alltests():
        lib.log.debug("[RUNNING] %s", mod)
        status, stdout, stderr = runone("pyrun " + mod)
        print(stdout)
        print(stderr)
        results[mod] = (status, stdout, stderr)
        lib.log.debug("[EXIT CODE] %s", status)
        if status != 0:
            lib.log.debug("Test finished with error code, stopping...")
            break
    return results


def main():
    if any(x != 0 for x, _, _ in runall().values()):
        raise RuntimeError("One or more tests failed. See log for more info.")
    else:
        lib.log.debug("All tests passed.")

