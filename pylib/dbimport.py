from db import do
import log
import webobject


TABLES = {
    'web_objects' : """
        CREATE TABLE IF NOT EXISTS `web_objects` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `name`),
            KEY object_by_category (`category`)
        ) ENGINE = MYISAM;
    """,

    'web_attributes' : """
        CREATE TABLE IF NOT EXISTS `web_attributes` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `attr` VARCHAR(20) NOT NULL,
            `value` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `name`, `attr`),
            KEY attribute_by_category_name (`category`, `name`(15))
        ) ENGINE = MYISAM;
    """,

    'web_connections' : """
        CREATE TABLE IF NOT EXISTS `web_connections` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `category` VARCHAR(15) NOT NULL,
            `category1` VARCHAR(15) NOT NULL,
            `name1` VARCHAR(255) NOT NULL,
            `category2` VARCHAR(15) NOT NULL,
            `name2` VARCHAR(255) NOT NULL,
            `attr` VARCHAR(15) NOT NULL,
            `value` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_index` (`category`, `category1`, `name1`(15), `category2`, `name2`(15), `attr`),
            INDEX `category_index` (`category`),
            KEY connection_by_category1_name1 (category1, name1(15)),
            KEY connection_by_category2_name2 (category2, name2(15))
        ) ENGINE = MYISAM;
    """,

    'web_events' : """
        CREATE TABLE IF NOT EXISTS `web_events` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `eventid` VARCHAR(15) NOT NULL,
            `userid` VARCHAR(15) NOT NULL,
            `entrytime` DATETIME NOT NULL,
            `eventstate` VARCHAR(15) NOT NULL,
            `action` VARCHAR(15) NOT NULL,
            `category` VARCHAR(15) NOT NULL,
            `refcategory` VARCHAR(15) NOT NULL,
            `category1` VARCHAR(15) NOT NULL,
            `name1` VARCHAR(255) NOT NULL,
            `category2` VARCHAR(15) NOT NULL,
            `name2` VARCHAR(255) NOT NULL,
            `field` VARCHAR(15) NOT NULL,
            `oldvalue` TEXT NOT NULL,
            `newvalue` TEXT NOT NULL,
            PRIMARY KEY (`id`),
            INDEX `category_index` (`category`),
            INDEX `user_index` (`userid`),
            KEY event_by_category1_name1 (category1, name1(15)),
            KEY event_by_category2_name2 (category2, name2(15))
        ) ENGINE = MYISAM;
    """,

    'web_counters' : """
        CREATE TABLE IF NOT EXISTS `web_counters` (
            `id` VARCHAR(15) NOT NULL,
            `value` INT,
            PRIMARY KEY (`id`)
        ) ENGINE = MYISAM;
    """,
}


def create_tables():
    for key, query in TABLES.iteritems():
        do(query)


def import_stories():
    q = """
        SELECT StoryID, Title, Description, Director, StoryWriter, Airdate, Stardate
        FROM `meta_ext_episodes_all`
    """
    qq = []
    attr_values = []
    obj_values = []

    for sid, t, desc, direct, sw, ad, sd in do(q):
        desc += """
Director: %s
Writer: %s
Stardate: %s
""" % (direct, sw, sd)

        sid = sid.encode("utf-8")
        t = t.encode("utf-8")
        desc = desc.encode("utf-8")
        ad = str(ad).encode("utf-8")

        attr_values.append(('story', sid, 'title', t))
        attr_values.append(('story', sid, 'description', desc))
        attr_values.append(('story', sid, 'date', str(ad)))
        obj_values.append(('story', sid))

        print obj_values[-1]

    do("INSERT INTO `web_attributes` (`category`, `name`, `attr`, `value`) "
       "values(%s, %s, %s, %s)", attr_values)

    do("INSERT INTO `web_objects` (`category`, `name`) "
       "values(%s, %s)", obj_values)


def import_storythemes():
    q = """
        SELECT StoryID, FieldName, Keyword, Comment
        FROM `master_all_exploaded`
        WHERE FieldName LIKE '%Theme%'
    """
    attr_values = []

    for sid, fn, theme, comment in do(q):
        sid = sid.lower()
        cmm = fn.split()[0].lower()

        attr_values.append(("featureof", "story", sid, "theme", theme, "weight", cmm))
        attr_values.append(("featureof", "story", sid, "theme", theme, "motivation", comment))

    do("REPLACE INTO `web_connections` (`category`, `category1`, `name1`, "
       "`category2`, `name2`, `attr`, `value`) "
       "values(%s, %s, %s, %s, %s, %s, %s)", attr_values)


def import_testevents():
    attr_values = [
        ("e.test.1", "odinlake", "2016-06-16 10:11:12", "edit", "event", "", 
            "story", "tng1x01", "", "", 
            "description", "nothing", "something", "reverted"  ),
        ("e.test.2", "odinlake", "2016-06-16 13:12:11", "new", "event", "featureof", 
            "story", "tos2x02", "theme", "obsession", 
            "weight", "", "choice", "merged"  ),
        ("e.test.3", "odinlake", "2016-06-16 15:15:15", "edit", "event", "featureof", 
            "story", "tng7x02", "theme", "redemption", 
            "motivation", "", "motivation goes here", "pending" ),
    ]
    fields = [
        "eventid",
        "userid",
        "entrytime",
        "action",
        "category",
        "refcategory",
        "category1",
        "name1",
        "category2", 
        "name2",
        "field", 
        "oldvalue", 
        "newvalue",
        "eventstate",
    ]
    fstr = ", ".join('`%s`' % s for s in fields)
    vstr = ", ".join("%s" for s in fields)

    do("REPLACE INTO `web_events` (%s) values (%s)" % (fstr, vstr), attr_values)


def import_counters():
    do("INSERT INTO `web_counters` (id, value) values (%s, %s)" , [
        ("event", 0),
    ])


def initial_import():
    do("DROP table web_events")

    create_tables()
    #import_counters()

    #import_testevents()
    #import_stories()
    #import_storythemes()

    for obj in webobject.TSTPEvent.load():
        print obj


if __name__ == '__main__':
    initial_import()





