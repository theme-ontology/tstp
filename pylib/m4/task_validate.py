import lib.log
import credentials
import os
import sys


def main():
    lib.log.info("task starting")
    lib.log.LOGTARGET.flush()

    gitpath = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
    os.chdir(gitpath)
    os.system("git pull")
    import webtask.test_integrity
    webtask.test_integrity.NOTESPATH = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
    webtask.test_integrity.main()

    sys.stdout.flush()
    sys.stderr.flush()
    lib.log.LOGTARGET.flush()
    lib.log.info("task finished")

