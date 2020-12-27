import os.path
import credentials
import m4.tasks
import lib.commits
import viz.stories_by_year
from shutil import copyfile


def main():
    with m4.tasks.ctx():
        path = os.path.join(credentials.TEMP_PATH, "sby_{}.svg")
        lib.commits.dbstore_commit_data(fromdate=None, recreate=False, quieter=False)
        outpath = viz.stories_by_year.make_animation(path)
        pubpath = os.path.join(credentials.PUBLIC_DIR, "tstpviz", "animated_stories_by_year.gif")
        copyfile(outpath, pubpath)