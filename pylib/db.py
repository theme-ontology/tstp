import MySQLdb as sql

from credentials import DBS
import log


DB_HANDLE = None
DB_HANDLES = {}


def connect(name = 'tstp'):
    ''' 
	Establish and cache connection to a named database.
	'''
    global DB_HANDLE

    try:
        if not name in DB_HANDLES:
            db = DBS[name]
            DB_HANDLES[name] = sql.connect(
				host = db['host'], 
				user = db['user'], 
				passwd = db['password'], 
				db = db['db'], 
				use_unicode = True, 
				charset = "utf8",
			)

    except Exception, ex:
        log.error("ERROR: Unable to connect to \"%s\":\n%s" % (name, str(ex)))
        raise

    DB_HANDLE = DB_HANDLES[name]


def handle():
    """
    Handle to currently selected db.
    """
    global DB_HANDLE

    if DB_HANDLE is None:
        connect()

    if DB_HANDLE is None:
        raise RuntimeError, "Failed to establish db connection"

    return DB_HANDLE


def cursor():
    """
    A cursor to currently selected db.
    """
    dbh = handle()
    return dbh.cursor()


def esc(*args):
    """
    SQL escape string.
    """
    if len(args) > 1:
        return tuple(esc(a) for a in args)
    return handle().escape_string(args[0])


def do(query, values = None, dofetch = True, quietish = False):
    '''
	Perform sql query and return result.
	'''
    con = cursor()

    if not quietish:
        log.info( 'Executing: %s...' % query )

    with log.Timer() as tt:
        if not values:
            res = con.execute( query )
        else:
            res = con.executemany( query, values )

        DB_HANDLE.commit()

    if not quietish:
        log.info( '...Done in %.4s seconds with result %s' % ( tt.elapsed / 1000.0, res ) )

    if dofetch and not values:
        return con.fetchall()

    return None


def uuid(name):
    """Get unique int in named wheel."""
    con = cursor()
    do("""
        UPDATE web_counters SET value=last_insert_id(value+1) WHERE id="%s"
    """ % name)
    return do("""SELECT last_insert_id()""")[0][0]


def test():
    query = '''SELECT * FROM aliens_tos'''

    for row in do(query):
        log.debug('%s' % str(row))


if __name__ == '__main__':
    print uuid("event")
    #test()
