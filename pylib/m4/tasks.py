import sys
from contextlib import contextmanager
import lib.log


@contextmanager
def ctx():
    lib.log.info("task starting")
    lib.log.LOGTARGET.flush()
    yield {}
    sys.stdout.flush()
    sys.stderr.flush()
    lib.log.LOGTARGET.flush()
    lib.log.info("task finished")


