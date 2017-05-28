'''
Created on June 5, 2016

@author: Mikael
'''
from datetime import datetime
import timeit


LEVELS = [ 'DEBUG', 'STATUS', 'INFO', 'ERROR', 'SILENT' ]
LEVEL = 0
LOGFILE = None


def set_logfile(filename):
    global LOGFILE
    LOGFILE = filename


def set_level(level):
    global LEVEL
    LEVEL = LEVELS.index(level)


def printmsg( msg, level = 'INFO' ):
    dt = datetime.now()
    tstr = dt.strftime( '%m/%d %H:%M:%S' )
    msg = unicode(msg).encode('ascii','ignore')

    if LOGFILE is not None:
        with open(LOGFILE, "a") as fh:
            fh.write(msg)
            fh.write("\n")

    if LEVELS.index(level) >= LEVEL:
        try:
            print( u'%-6s %s  %s' % ( level, tstr, msg ) )
        except:
            print "<failed to print>"


def debug( msg ):
    printmsg( msg, 'DEBUG' )

def status( msg ):
    printmsg( msg, 'STATUS' )

def info( msg ):
    printmsg( msg, 'INFO' )

def error( msg ):
    printmsg( msg, 'ERROR' )


class Timer( object ):
    def __init__( self, verbose = False ):
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
            print 'elapsed time: %f ms' % self.elapsed
