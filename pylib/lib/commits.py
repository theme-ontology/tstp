from __future__ import print_function
from collections import defaultdict
from credentials import GIT_THEMING_PATH_HIST
import os
import subprocess
from lib.dates import iter_days
import lib.files
from dateutil.parser import parse
import re
import lib.dataparse


DEBUG = False


def get_story_prefixes(basepath):
    """
    Return counts for each SID prefix present in the dataset.
    """
    prefixes = defaultdict(int)
    for path in lib.files.walk(basepath, ".*\.(st)\.txt$", 0):
        if path.endswith(".st.txt"):
            for obj in lib.dataparse.read_stories_from_txt(path, False):
                cat = re.match(r"([A-Za-z]+)", obj.name).group(1)
                prefixes[cat] += 1
    return dict(prefixes)


def get_datapoint(basepath):
    """
    Return statistics about the repository as it is at location "basepth".
    """
    prefixes = get_story_prefixes(basepath)
    counts = defaultdict(set)
    data = defaultdict(float)

    for k, v in prefixes.items():
        data["prefix:"+k] = v

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$", 0):
        if path.endswith(".th.txt"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            counts["themes"].update(o.name for o in objs)
        if path.endswith(".st.txt"):
            objs = list(lib.dataparse.read_stories_from_txt(path, False))
            counts["stories"].update(o.name for o in objs)

    data["themes"] = len(counts["themes"])
    data["stories"] = len(counts["stories"])
    return data


def list_commits(basepath):
    """
    Return a list of all commits ever done in repository.
    """
    subprocess.check_output('git checkout HEAD'.split()).decode("utf-8")
    gitlog = subprocess.check_output('git log --no-merges --all'.split()).decode("utf-8")
    entries = []
    commit, author, date = None, None, None

    for line in gitlog.split("\n"):
        if line.startswith("commit ") and not commit:
            commit = line.strip().split()[-1]
            author, date = None, None
        if line.startswith("Author: "):
            author = line.strip().split()[1]
        if line.startswith("Date: "):
            date = line[5:].strip()
        if not line.strip() and commit:
            entries.append((commit, author, parse(date, ignoretz=True)))
            commit, author, date = None, None, None

    entries.sort(key=lambda x: x[-1])
    return entries


def get_commits_data():
    """
    Return information about the state of the repository for regularly spaced dates,
    by default Friday midnights every week.
    :return:
    """
    basepath = GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    os.chdir(basepath)

    entries = list_commits(basepath)
    prefixes = get_story_prefixes(basepath)
    data = []
    prefixes = sorted(((v, k) for k, v in prefixes.items()), reverse=True)
    prefixset = set(k for _, k in prefixes[:20])
    dt1 = entries[0][-1]
    dt2 = entries[-1][-1]
    dtiter = iter_days(dt1, dt2, "fri", "00:00")
    # dtiter = iter_days("2019-07-01", dt2, "fri", "00:00") # debug
    atdt = next(dtiter)

    for idx, (commit, author, date) in enumerate(entries):
        if DEBUG:
            if date < parse("2018-12", ignoretz=True): continue  # debug
            if len(data) > 60: break  # debug
        while atdt < date:
            try:
                atdt = next(dtiter)
            except StopIteration:
                atdt = None
                break
        if atdt is None:
            break

        if idx < len(entries) - 1:
            if atdt >= entries[idx+1][-1]:
                continue
        # date must be the last viable date less than atdt
        print(date.isoformat(), commit)
        print("Evaluating for: {}...".format(atdt.isoformat()))
        res = None

        try:
            #res = subprocess.check_output(['git', 'checkout', commit], stderr=open(os.devnull, 'wb')).decode("utf-8")
            res = subprocess.check_output(['git', 'checkout', '-f', commit]).decode("utf-8")
        except Exception as e:
            print("GIT ERROR", e)
            print(res, "...")
            continue
        try:
            datapoint = get_datapoint(notespath)
            nthemes = datapoint["themes"]
        except Exception as e:
            print("PARSE ERROR", e)
            continue
        if (nthemes > 500):
            data.append((atdt, datapoint))
            print(data[-1])

    return data


def dbstore_commit_data(recreate=False):
    import dbdefine
    import db
    import json

    dbdefine.create_tables(subset={"commits_stats"}, recreate=recreate)
    donerevs = set(x[0] for x in db.do("""SELECT id FROM commits_stats"""))

    basepath = GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    os.chdir(basepath)
    entries = list_commits(basepath)

    for idx, (commit, author, date) in enumerate(entries):
        if commit in donerevs:
            print("EXISTS:", (commit, author, date), "...SKIPPING")
        else:
            try:
                datapoint = get_datapoint(notespath)
            except Exception as e:
                print("PARSE ERROR", e)
                raise
                continue
            data = json.dumps(datapoint)
            row = (commit, date.strftime('%Y-%m-%d %H:%M:%S'), author, data)
            db.do("""INSERT INTO commits_stats VALUES(%s, %s, %s, %s)""", values=[row])
            print("INSERTED: ", str(row)[:120], "...")


def main():
    dbstore_commit_data(False)









