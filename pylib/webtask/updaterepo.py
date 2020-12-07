import cgitb; cgitb.enable()
from credentials import GIT_THEMING_PATH
import os
import os.path
import lib.log


def runcmd(cmd):
    lib.log.info("EXEC: %s", cmd)
    os.system(cmd)


def update_repo():
    path = os.path.join(GIT_THEMING_PATH, "notes")
    os.chdir(path)
    runcmd("git reset --hard origin/master")
    runcmd("git pull --depth=1 --allow-unrelated-histories")


def main():
    update_repo()


