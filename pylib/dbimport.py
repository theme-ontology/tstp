from db import do
import log
import webobject
from dbdefine import create_tables



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
    if False:
        initial_import()





