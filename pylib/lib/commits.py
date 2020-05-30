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
import dbdefine
import db
import json
import sys
import lib.datastats

DEBUG = False


def get_story_prefixes(basepath, verbose=False):
    """
    Return counts for each SID prefix present in the dataset.
    """
    prefixes = defaultdict(lambda: defaultdict(int))
    dates = {}
    undef = set()
    baddates = {}
    badsids = set()
    counted = set()

    for path in lib.files.walk(basepath, ".*\.(st)\.txt$", 0):
        if path.endswith(".st.txt"):
            for story in lib.dataparse.read_stories_from_txt(path, False):
                dates[story.name.strip()] = story.date

    for path in lib.files.walk(basepath, ".*\.(st)\.txt$", 0):
        if path.endswith(".st.txt"):
            for story in lib.dataparse.read_storythemes_from_txt(path, False):
                if story.name1 not in counted:
                    counted.add(story.name1)
                    cat = re.match(r"([A-Za-z]+)", story.name1)
                    if not cat:
                        badsids.add(story.name1)
                    else:
                        cat = cat.group(1)
                        year = None
                        if story.name1 in dates:
                            try:
                                year = int(dates[story.name1][:4])
                            except ValueError:
                                baddates[story.name1] = dates[story.name1]
                        else:
                            siddate = re.search(r"\(([0-9]{4})\)$", story.name1)
                            if siddate:
                                year = int(siddate.group(1))
                            else:
                                undef.add(story.name1)
                        if year:
                            prefixes[cat][year] += 1
    if verbose:
        if undef:
            print("UNDEFINED SIDS:", sorted(undef))
        if baddates:
            print("BAD DATES:", baddates)
        if badsids:
            print("BAD SIDS:", badsids)
    return dict(prefixes)


def get_datapoint(basepath):
    """
    Return statistics about the repository as it is at location "basepth".
    """
    prefixes = get_story_prefixes(basepath)
    counts = defaultdict(set)
    data = {}
    themes = []

    for k, v in prefixes.items():
        data["prefix:"+k] = dict(v)

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$", 0):
        if path.endswith(".th.txt"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            themes.extend(objs)
            counts["themes"].update(o.name for o in objs)
        if path.endswith(".st.txt"):
            tobjs = lib.dataparse.read_storythemes_from_txt(path, False)
            objs = list(lib.dataparse.read_stories_from_txt(path, False))
            counts["stories"].update(o.name for o in objs)
            counts["themedstories"].update(o.name1 for o in tobjs)

    parents, children, bfs = lib.datastats.construct_theme_tree(themes)
    levels = lib.datastats.construct_metathemes_by_level(parents, children, bfs, withLeaves=True, allRoots=True)
    for nn in range(6):
        data["themesL%s" % nn] = len(levels[nn]) if nn < len(levels) else 0
    data["themesLP"] = sum(len(level) for level in levels[6:])
    data["themes"] = len(counts["themes"])
    data["stories"] = len(counts["stories"])
    data["themedstories"] = len(counts["themedstories"])
    return dict(data)


def list_commits(basepath):
    """
    Return a list of all commits ever done in repository.
    """
    subprocess.check_output('git fetch origin'.split()).decode("utf-8")
    subprocess.check_output('git reset --hard origin/master'.split()).decode("utf-8")
    gitlog = subprocess.check_output(
        'git log --no-merges --all --date=local'.split(),
        env=dict(os.environ, TZ="UTC")
    ).decode("utf-8")
    entries = []
    commit, author, date = None, None, None

    for ii, line in enumerate(gitlog.split("\n")):
        if line.startswith("commit ") and not commit:
            commit = line.strip().split()[-1]
            author, date = None, None
        if line.startswith("Author: "):
            try:
                author = re.match("^Author: ([^<>]+)", line).group(1).strip()
            except:
                print("UNEXPECTED Author format: " + line)
                author = line.strip().split()[1]
        if line.startswith("Date: "):
            date = line[5:].strip()
        if not line.strip() and commit:
            entries.append([commit, author, parse(date, ignoretz=True), ""])
            commit, author, date = None, None, None

        if not commit and line.startswith("    ") and entries:
            entries[-1][-1] += line[4:] + "\n"

    entries.sort(key=lambda x: x[2])
    return entries


def get_commits_data(period='weekly'):
    """
    Return information about the state of the repository for regularly spaced dates,
    by default Friday midnights every week.
    :return:
    """
    entries = list(db.do("""
        SELECT id, time, author, stats FROM commits_stats
        ORDER BY time ASC
    """))
    dt1 = entries[0][1]
    dt2 = entries[-1][1]
    if period == 'weekly':
        dtiter = iter_days(dt1, dt2, daysofweek="fri", attime="00:00")
    elif period == 'daily':
        dtiter = iter_days(dt1, dt2, attime="00:00")
    else:
        raise ValueError("Bad period: {}".format(period))
    atdt = next(dtiter)
    data = []

    for idx, (commit, date, author, sdata) in enumerate(entries):
        while atdt < date:
            try:
                atdt = next(dtiter)
            except StopIteration:
                atdt = None
                break
        if atdt is None:
            break

        if idx < len(entries) - 1:
            if atdt >= entries[idx+1][1]:
                continue
        # date must be the last viable date less than atdt
        datapoint = json.loads(sdata)
        nthemes = datapoint["themes"]
        if nthemes > 500:
            data.append((atdt, datapoint))

    return data


def dbstore_commit_data(fromdate=None, recreate=False, quieter=False):
    """
    Store data for the last commit each date.
    """
    dbdefine.create_tables(subset={"commits_stats", "commits_log"}, recreate=recreate)
    commits = list(db.do("""SELECT id, time FROM commits_stats"""))
    donerevs = set(x[0] for x in commits)
    if not commits:
        fromdate = None
    if fromdate == "<latest>":
        fromdate = max(x[1] for x in commits)
    basepath = GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    os.chdir(basepath)
    entries = list_commits(basepath)
    bydate = defaultdict(list)
    latestcommits = set()
    logrows = [ (commit, date, author, msg) for commit, author, date, msg in entries ]

    db.do("""REPLACE INTO commits_log VALUES(%s, %s, %s, %s)""", values=logrows)

    for commit, _, date, _ in entries:
        bydate[date.date()].append((date, commit))
    for datelist in bydate.values():
        date, commit = max(datelist)
        latestcommits.add(commit)

    for idx, (commit, author, date, _) in enumerate(entries):
        if fromdate and date <= fromdate:
            if not quieter:
                print("EARLIER:", (commit, author, date), "...SKIPPING")
        elif commit in donerevs:
            if not quieter:
                print("EXISTS:", (commit, author, date), "...SKIPPING")
        elif commit not in latestcommits:
            if not quieter:
                print("SKIPPING EARLIER COMMIT:", (commit, author, date))
        else:
            try:
                # res = subprocess.check_output(['git', 'checkout', commit], stderr=open(os.devnull, 'wb')).decode("utf-8")
                res = subprocess.check_output(['git', 'checkout', '-f', commit]).decode("utf-8")
            except Exception as e:
                print("GIT ERROR", repr(e))
                continue
            try:
                datapoint = get_datapoint(notespath)
            except AssertionError as e:
                print("PARSE ERROR", repr(e))
                continue
            except Exception as e:
                print("UNKNOWN ERROR", repr(e))
            data = json.dumps(datapoint)
            row = (commit, date.strftime('%Y-%m-%d %H:%M:%S'), author, data)
            db.do("""REPLACE INTO commits_stats VALUES(%s, %s, %s, %s)""", values=[row])
            if not quieter:
                print("INSERTED: ", str(row)[:120], "...")
                print(dict(datapoint))


def main():
    basepath = GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    if '--test' in sys.argv:
        data = get_datapoint(notespath)
        from pprint import pprint
        pprint(data)
    else:
        fromdate = None if "-a" in sys.argv else "<latest>"
        recreate = '-x' not in sys.argv
        #import datetime; fromdate = datetime.datetime(2020, 5, 15, 0, 0, 0)
        dbstore_commit_data(fromdate=fromdate, recreate=recreate)









