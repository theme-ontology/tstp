from __future__ import print_function
import os
from credentials import GIT_THEMING_PATH_HIST
import lib.commits
import lib.files
import lib.dataparse
from git import Repo

#' preliminaries
basepath = GIT_THEMING_PATH_HIST
notespath = os.path.join(basepath, "notes")
os.chdir(basepath)

#' checkout git repo at a given commid id or version tag
#commit_id = '56b4640d27b6f78478cd6aada1189add3480bf17'
version_tag = 'v0.3.2'
repo = Repo(GIT_THEMING_PATH_HIST)
#repo.git.checkout(commit_id)
repo.git.checkout(version_tag)

#' read theme files
deprecated_themes_file = 'deprecated-themes.txt'
theme_files = list(lib.files.walk(basepath, ".*\.th\.txt$"))
print("\n".join(theme_files))
#print(theme_files)

themes = list(lib.dataparse.read_themes_from_txt(theme_files[0], False))
print(themes[0])

