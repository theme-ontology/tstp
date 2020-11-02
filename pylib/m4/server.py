import credentials
from datetime import datetime, date
from flask import Flask, request
import lib.log
import logging
import os.path
import os
import subprocess
import threading
import time
import sys
from collections import defaultdict
import json
import lib.files
from urllib import unquote_plus


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
PROCLIST = {}
TASKLIST = {
    "validate": "validate-git-repository-notes",
    "monitorgit": "monitor-git-repository-notes",
    "challenge": "create-creative-challenge",
    "importgit": "import-git-repository-notes",
}
TASKEXPLAIN = {
    "validate": """
Pull the latest version of https://github.com/theme-ontology/theming
and perform a variety of tests on it. This is done periodically, and
when github's webhook reports that the repository changed.
    """,
    "monitorgit": """
Records commits to https://github.com/theme-ontology/theming and sends
emails with diffs. This is done 30 min after github's webhook reports 
that the repository changed, the timer being reset if the repository
changes within that interval.
    """,
    "challenge": """
    Assemble a creative challenge in the form of a list of interesting
    themes for which the participant is to write a matching story. This
    task triggers only once per week, targeted for Saturday.
        """,
    "importgit": """
This task will perform the import pipeline: Pull 
https://github.com/theme-ontology/theming, validate it, load all data
and store it in the local SQL db, cache various queries and compute
some final statistics. It can only be started manually. 
    """,
}
taskcount = defaultdict(int)
LOGPATH = os.path.join(credentials.PUBLIC_DIR, "m4", "logs", "m4.log")
SCHEDULER = {}
LAST_STATUS = {}
LOGS = {}


class TaskTimer(threading.Thread):
    """
    A simple timer that calls the given function at regular intervals.
    """
    def __init__(self, func, delay, repeating=False, nowAndRepeat=False):
        super(TaskTimer, self).__init__()
        self.func = func
        self.delay = delay
        self.repeating = repeating or nowAndRepeat
        self.nowAndRepeat = nowAndRepeat
        self.active = True
        self.setDaemon(True)
        self.start()
        self.nextalarm = 0

    def reset(self, newdelay=None):
        if newdelay:
            self.delay = newdelay
        self.nextalarm = time.time() + self.delay

    def run(self):
        time.sleep(1.0)
        if self.active and self.nowAndRepeat:
            self.func()
        while self.active:
            self.reset()
            while time.time() < self.nextalarm:
                time.sleep(1.0)
            if self.active:
                self.func()
            if not self.repeating:
                self.stop()

    def stop(self):
        self.active = False


def now():
    """
    Returns:
    String representation of current time.
    """
    return datetime.now().isoformat().replace("T", " ")


def getlogpath(name, newversion=True):
    """
    Return path to logfile for a subtask.

    Args:
        name: name of a task.

    Returns:
        path to logfile for task.
    """
    version, outpath = None, None  # shut lint up
    def mkpath(today, name, version):
        return os.path.join(credentials.PUBLIC_DIR, "m4", "logs", "%s-%s.%03d.log" % (
            today, name, version))
    today = date.today().isoformat().replace("-", "")
    for version in range(0, 1000):
        outpath = mkpath(today, name, version)
        if not os.path.isfile(outpath):
            break
    if newversion and version < 1000:
        return outpath
    else:
        return mkpath(today, name, version-1)


def checktask(name, terminate=False):
    """
    Check on, and optionally stop, a subtask.

    Args:
        name: Name of a subtask, see function subtask.
        terminate: If True, seek to terminate the subtask if it is running.

    Returns:
        True if subtask is still running, False otherwise.
    """
    if name in PROCLIST:
        p, fh = PROCLIST[name]
        if p.poll() is None:
            return True
        lib.log.info("[%s] previous task ended with code %s" % (
            name, p.returncode))
        LAST_STATUS[name] = [
            now(),
            p.returncode,
        ]
        fh.close()
        del PROCLIST[name]
    return False


def checktasks():
    """
    Go through all currently ctive tasks and see if they are done.
    Cleanup and update statuses if so.
    """
    for name in list(PROCLIST):
        checktask(name)


def runtask(name):
    """
    Run a name task as a subprocess. The task must exist as a python
    file at "m4.task_[name]".

    Args:
        name: a string that corresponds to an existing m4.task_ python file.

    Returns:
        A string explaining what happened.
    """
    msg = ""
    if name not in TASKLIST:
        msg = "[%s] no such task available" % name
    elif checktask(name):
        msg = "[%s] previous task still running" % name
    else:
        cmd = ["pyrun", "m4.task_%s" % name]
        outpath = getlogpath(name)
        LOGS[name] = outpath
        fhlog = open(outpath, "a+")
        fhlog.seek(0, os.SEEK_END)
        p = subprocess.Popen(" ".join(cmd), stdout=fhlog, stderr=fhlog, shell=True)
        PROCLIST[name] = (p, fhlog)
        LAST_STATUS[name] = ["running", "n/a"]
        taskcount[name] += 1
        msg = "[%s] started task, logging in %s" % (name, outpath)
    lib.log.info(msg)
    return msg


def scheduletask(name, delay=60.0):
    """
    Schedule a task to start in _delay_ seconds. Any previously
    scheduled task of the same time will be cancelled.

    Args:
        name: name of task.
        delay: seconds to wait.
    """
    if name not in SCHEDULER or not SCHEDULER[name].active:
        SCHEDULER[name] = TaskTimer(lambda: runtask(name), delay)
    SCHEDULER[name].reset(delay)
    lib.log.info("[%s] scheduled task to run in %s seconds" % (name, delay))
    return "scheduled"


@app.route("/")
def root():
    lib.log.info("manual ping from %s", request.remote_addr)
    return ping()


@app.route("/ping")
def ping():
    return "ALIVE: " + datetime.now().isoformat().replace("T", " ")


@app.route("/task/validate")
def task_validate():
    scheduletask("validate", 10.0)
    return "[OK]"


@app.route("/task/monitorgit")
def task_monitorgit():
    scheduletask("monitorgit", 10.0)
    return "[OK]"


@app.route("/task/importgit")
def task_importgit():
    scheduletask("importgit", 15.0)
    return "[OK]"


@app.route("/event/gitchanged")
def event_gitchanged():
    scheduletask("validate", 15.0)
    scheduletask("monitorgit", 1800.0)
    return "[OK]"


@app.route("/status")
def status():
    sys.stdout.flush()
    sys.stderr.flush()
    res = ping() + "\n"
    if os.path.isfile(LOGPATH):
        with open(LOGPATH, "r") as fh:
            res += fh.read()
    return json.dumps({
        "m4log": res,
        "status": "Functioning Within Normal Parameters",
        "subtasks": [
            {
                "name": TASKLIST.get(name, ""),
                "shortname": name,
                "pingurl": "m4notify?name=%s" % name,
                "status": LAST_STATUS.get(name, ["n/a", "unknown"]),
                "running": 1 if name in PROCLIST else 0,
                "logpath": lib.files.path2url(LOGS.get(name, "")),
                "explain": TASKEXPLAIN.get(name, "n/a")
            }
            for name in TASKLIST
        ],
    })


@app.route("/tool/gitsearch", methods=['POST', 'GET'])
def event_gitsearch():
    from util.searchgithistory import find_githistory
    query = unquote_plus(request.form.get("query"))
    lib.log.info("find_githistory: %s (starting)", query)
    data = find_githistory(query)
    lib.log.info("find_githistory: %s (done)", query)
    return json.dumps({
        "data": data,
    })


def main():
    os.environ["PYTHONUNBUFFERED"] = "1"
    timed_tasks = [
        TaskTimer(task_validate, 3600 * 8, repeating=True),
        TaskTimer(checktasks, 1.0, repeating=True),
        TaskTimer(lambda: scheduletask("challenge", 5.0), 3600 * 8, nowAndRepeat=True),
    ]
    app.run(host="127.0.0.1", port="31985")
    for task in timed_tasks:
        task.stop()
    for name in list(PROCLIST):
        checktask(name, terminate=True)







