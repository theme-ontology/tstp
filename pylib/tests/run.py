import sys
import os.path
import lib.files
import subprocess
import lib.log


def main():
    mod = sys.modules[__name__]
    base = os.path.split(mod.__file__)[0]
    nstem = len(lib.files.split(base)) - 1
    for path in lib.files.walk(base, "test_.*\\.py$"):
        parts = lib.files.split(path)
        print(parts)
        mod = '.'.join(parts[nstem:-1] + [parts[-1][:-3]])
        lib.log.debug("[RUNNING] %s", mod)
        status = subprocess.call("pyrun " + mod, shell=True)
        lib.log.debug("[EXIT CODE] %s", status)
        if status != 0:
            lib.log.debug("Test finished with error code, stopping...")
            break


