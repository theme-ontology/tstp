import db
import dbdefine
import log
import sys


def migrate(fromdb, todb):
    db.connect(todb)
    dbdefine.create_tables()
    
    for table in dbdefine.TABLES:
        db.connect(fromdb)
        rows = []
        
        for row in db.do("SELECT * FROM `%s`" % table):
            rows.append(row)
            
        log.info("Read %d rows from %s@%s", len(rows), table, fromdb)
    
        if rows:
            db.connect(todb)
            vpatt = ', '.join("%s" for _ in rows[0])
            db.do("INSERT INTO `%s` VALUES (%s)" % (table, vpatt), rows)
            log.info("Wrote %d rows to %s@%s", len(rows), table, todb)



if __name__ == '__main__':
    fromdb = sys.argv[1]
    todb = sys.argv[2]
    migrate(fromdb, todb)
    
    



