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


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
phandles = {}
TASKLIST = {
    "validate": "validate-git-repository-notes",
}
taskcount = defaultdict(int)
LOGPATH = os.path.join(credentials.PUBLIC_DIR, "m4", "logs", "m4.log")
SCHEDULER = {}
STATUS = {}
LOGS = {}


class TaskTimer(threading.Thread):
    """
    A simple timer that calls the given function at regular intervals.
    """
    def __init__(self, func, delay, repeating=False):
        super(TaskTimer, self).__init__()
        self.func = func
        self.delay = delay
        self.repeating = repeating
        self.active = True
        self.setDaemon(True)
        self.start()
        self.nextalarm = 0

    def reset(self):
        self.nextalarm = time.time() + self.delay

    def run(self):
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
    return datetime.now().isoformat().replace("T", " ");


def getlogpath(name, newversion=True):
    """
    Return path to logfile for a subtask.

    Args:
        name: name of a task.

    Returns:
        path to logfile for task.
    """
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
    if name in phandles:
        p, fh = phandles[name]
        if p.poll() is None:
            return True
        lib.log.info("[%s] previous task ended with code %s" % (
            name, p.returncode))
        STATUS[name] = [
            now(),
            p.returncode,
        ]
        fh.close()
        del phandles[name]
    return False


def checktasks():
    """
    Go through all currently ctive tasks and see if they are done.
    Cleanup and update statuses if so.
    """
    for name in list(phandles):
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
        phandles[name] = (p, fhlog)
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
    SCHEDULER[name].reset()
    lib.log.info("[%s] scheduled task to run in %.2s seconds" % (name, delay))
    return "scheduled"


def path2url(path):
    """
    Take a local path and convert it to a url by which the object is
    accessible, assuming it lies in the public dir.
    Returns: url
    """
    basepath = os.path.join(credentials.PUBLIC_DIR, "m4")
    if path.startswith(basepath):
        urlobj = path[len(basepath):].replace("\\", "/").strip("/")
        return credentials.SERVER_PUB_URL + "m4/" + urlobj
    return ""


@app.route("/")
def root():
    lib.log.info("manual ping from %s", request.remote_addr)
    return ping()


@app.route("/ping")
def ping():
    return "ALIVE: " + datetime.now().isoformat().replace("T", " ")


@app.route("/task/validate")
def validate():
    scheduletask("validate", 15.0)
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
        "subtasks": [
            {
                "name": TASKLIST.get(name, ""),
                "status": STATUS.get(name, ["n/a", "unknown"]),
                "logpath": path2url(LOGS.get(name, "")),
            }
            for name in TASKLIST
        ],
    })

def main():
    timed_tasks = [
        TaskTimer(validate, 3600 * 8, repeating=True),
        TaskTimer(checktasks, 1.0, repeating=True),
    ]
    app.run(host="127.0.0.1", port="31985")
    for task in timed_tasks:
        task.stop()
    for name in list(phandles):
        checktask(name, terminate=True)
