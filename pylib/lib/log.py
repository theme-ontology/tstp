'''
Created on June 5, 2016

@author: Mikael
'''
from datetime import datetime
import timeit
import sys
import codecs
import traceback

bin_stdout = sys.stdout
bin_stderr = sys.stderr

LEVELS = [ 'DEBUG', 'STATUS', 'INFO', 'WARN', 'ERROR', 'SILENT' ]
LEVEL = 0
LOGFILE = None
LOGTARGET = sys.stdout
LOGTARGETMODE = "utf-8"


def redirect(loc = "stderr"):
    global LOGTARGET
    LOGTARGET = getattr(sys, loc)


def set_templog(filename):
    import os
    import tempfile
    set_logfile(os.path.join(tempfile.gettempdir(), filename))
    debug("log location %s", LOGFILE)


def set_logfile(filename):
    global LOGFILE
    LOGFILE = filename


def set_level(level):
    global LEVEL
    LEVEL = LEVELS.index(level)


def set_logmode(mode = "utf-8"):
    global LOGTARGETMODE

    lt = "stderr" if LOGTARGET == sys.stderr else "stdout"

    if mode == "utf-8":
        sys.stdout = codecs.getwriter('utf8')(bin_stdout)
        sys.stderr = codecs.getwriter('utf8')(bin_stderr)
    elif mode == "binary":
        sys.stdout = bin_stdout
        sys.stderr = bin_stderr
    else:
        raise RuntimeError("no such mode: " + mode)

    LOGTARGETMODE = mode
    redirect(lt)


def printfunc(s):
    if LOGTARGETMODE == "binary":
        LOGTARGET.write(s.encode("utf-8", "replace"))
    else:
        LOGTARGET.write(s)
    LOGTARGET.write("\n")
    
    
def printmsg(msg, level = 'INFO', args = None):
    dt = datetime.now()
    tstr = dt.strftime( '%Y-%m-%d %H:%M:%S' )
    
    if args:
        msg = msg % args
    msg = unicode(msg).encode('ascii','ignore')
    logline = u'%-6s %s  %s' % (level, tstr, msg)
    
    if LOGFILE is not None:
        with open(LOGFILE, "a") as fh:
            fh.write(logline)
            fh.write("\n")

    if LEVELS.index(level) >= LEVEL:
        try:
            printfunc(logline)
        except:
            printfunc("<failed to print logline>")
            raise


def debug(msg, *args):
    printmsg(msg, 'DEBUG', args)

def status(msg, *args):
    printmsg(msg, 'STATUS', args)

def info(msg, *args):
    printmsg(msg, 'INFO', args)

def error(msg, exc_info=False, *args):
    exc_info = sys.exc_info()
    printmsg(msg, 'ERROR', args)
    traceback.print_exception(*exc_info)

def warn(msg, *args):
    printmsg(msg, 'WARN', args)


class Timer( object ):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.timer = timeit.default_timer

    def __enter__( self ):
        self.start = self.timer()
        return self

    def __exit__( self, *args ):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs
        if self.verbose:
            title = self.verbose if isinstance(self.verbose, basestring) else ""
            debug(title + ' ..elapsed time: %f ms' % self.elapsed)


class Mode( object ):
    def __init__(self, mode):
        self.mode = mode

    def __enter__( self ):
        self.old_mode = LOGTARGETMODE
        set_logmode(self.mode)
        return self

    def __exit__( self, *args ):
        set_logmode(self.old_mode)
        return self


#: set up default
set_logmode()
redirect("stderr")


