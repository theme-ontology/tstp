"""
Search through all git commits for any lines, added or deleted.
"""
import sys
import os
import credentials
import subprocess
import re
from dateutil.parser import parse


def find_githistory(pattern):
    basepath = credentials.GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    os.chdir(basepath)
    subprocess.check_output('git fetch origin'.split()).decode("utf-8")
    subprocess.check_output('git reset --hard origin/master'.split()).decode("utf-8")
    cmd = 'git log --no-merges --all --date=local -p'.split() + ['-G%s' % pattern]
    gitlog = subprocess.check_output(cmd, env=dict(os.environ, TZ="UTC")).decode("utf-8")
    hitlist = []

    for ii, line in enumerate(gitlog.split("\n")):
        #print(line)
        if line.startswith("commit "):
            commit = line.strip().split()[-1]
            author, date, filename = None, None, None
        if line.startswith("Author: "):
            try:
                author = re.match("^Author: ([^<>]+)", line).group(1).strip()
            except:
                print("UNEXPECTED Author format: " + line)
                author = line.strip().split()[1]
        if line.startswith("Date: "):
            date = line[5:].strip()
            dt = parse(date, ignoretz=True)
            fmtdate = dt.strftime("%Y-%m-%d %H:%M:%S")
        if line.startswith("--- a/"):
            fromfilename = line[6:]
        elif line.startswith("+++ b/"):
            intofilename = line[6:]
        elif line.startswith("++") or line.startswith("--"):
            pass
        elif line.startswith("+") or line.startswith("-"):
            filename = intofilename if line[0] == "+" else fromfilename
            if re.search(pattern, line):
                hitlist.append([commit, fmtdate, author, filename, line.strip()])

    return hitlist


def main():
    pattern = sys.argv[-1]
    hitlist = find_githistory(pattern)
    for entry in hitlist:
        print(entry)

