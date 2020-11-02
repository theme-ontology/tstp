import cgitb; cgitb.enable()
from credentials import GIT_THEMING_PATH
import os
import os.path


def update_repo():
    path = os.path.join(GIT_THEMING_PATH, "notes")
    os.chdir(path)
    os.system("git reset --hard origin/master")
    os.system("git pull --depth=1")


def main():
    update_repo()


