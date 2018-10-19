import cgitb; cgitb.enable()
from credentials import GIT_THEMING_PATH
import os
import os.path


def update_repo():
    path = os.path.join(GIT_THEMING_PATH, "notes")
    os.chdir(path)
    os.system("git pull")


def main():
    update_repo()
    os.system("pyrun util.db clear nowarn")
    os.system("pyrun util.db import %s" % path)



