from __future__ import print_function

import json
import datetime

from db import do, esc, uuid
import re

import six
if six.PY3:
    unicode = str
else:
    from itertools import izip


##################################################################
##
## A generic object type.
##
##################################################################
class TSTPObject(object):
    category = "object"
    fields = (
        "name",
        "category",
        "description",
    )
    extra_fields = ()
    indexes = (
        "name",
        "category",
    )

    def __init__(self, *args, **kwargs):
        extra_fields = []
        for field, value in zip(self.fields, args):
            setattr(self, field, value)
        for field, value in kwargs.items():
            setattr(self, field, value)
            if field not in self.fields:
                extra_fields.append(field)
        self.extra_fields = tuple(extra_fields)
            
    @classmethod
    def create(cls, **kwargs):
        """
        Key error on missing field value in kwargs; unlike __init__, 
        all fields must be set.
        """
        strict = True
        obj = cls()
        
        for kwarg in kwargs:
            if kwarg not in cls.fields:
                raise ValueError("Invalid field %s" % kwarg)
                
        for field in cls.fields:
            value = kwargs.get(field, None) 
            value = value if value is not None else getattr(cls, field, None)

            if value is not None or not strict:
                setattr(obj, field, "" if value is None else value)
            else:
                raise ValueError("Missing value for %s" % field)
            
        return obj

    def test_fields(self):
        """
        Check that all fields have been set.
        """
        for field in self.fields:
            if not hasattr(self, field):
                raise ValueError("Missing value for %s" % field)

    @classmethod
    def edit_object(cls, cat, name, attrs, vals):
        table = "web_attributes"
        dt = datetime.datetime.now()
        cat, name = esc(cat, name)
        attrstr = cls.sql_filter_list(attrs)
        #vals = [ esc(x) for x in vals_in ]
        oldvalue = None
        alu = dict(izip(attrs, vals))
        evidbase = "ev.%d-" % uuid("event")
        idx = 0

        events = []
        updates = []

        for attr, oldvalue in do("""
            SELECT attr, value FROM `%s` WHERE 
            category = "%s" AND name = "%s" AND attr IN %s
            LIMIT 1
        """ % (table, cat, name, attrstr)):
            evid = evidbase + str(idx)
            idx += 1
            newvalue = alu[attr]
            event = (evid, "odinlake", dt, "edit", "event", "", 
                cat, name, "", "", attr, oldvalue, newvalue, "pending")
            update = (cat, name, attr, newvalue)
            obj = (cat, name)

            events.append(event)
            updates.append(update)

        evfields = [
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
        fstr = ", ".join('`%s`' % s for s in evfields)
        vstr = ", ".join("%s" for s in evfields)
        do("REPLACE INTO `web_events` (%s) values (%s)" % (fstr, vstr), events)

        cls.commit_updates(updates)

    @classmethod
    def commit_updates(cls, updates):
        """
        Write multiple attribute updates for this class into the database
        without further ado. Dangerous.
        """
        chunksize = 10000
        attrfields = [
            "category",
            "name",
            "attr",
            "value",
        ]

        for i in range(0, len(updates), chunksize):
            updatechunk = updates[i:i + chunksize]
            objs = [ x[:2] for x in updatechunk ]
            fstr = ", ".join('`%s`' % s for s in attrfields)
            vstr = ", ".join("%s" for s in attrfields)
            do("REPLACE INTO `web_attributes` (%s) values (%s)" % (fstr, vstr), updatechunk)
            do("REPLACE INTO `web_objects` (`category`, `name`) values (%s, %s)", objs)

    @classmethod
    def sql_filter_list(cls, itemstr):
        if isinstance(itemstr, (str, unicode)):
            items = itemstr.split(',')
        else:
            items = itemstr

        parts = [ esc(item) for item in items ]
        ss = ', '.join("'%s'" % s for s in parts)
        return '(%s)' % ss

    @classmethod
    def query_for(cls, attrs, filters, table, limit):
        qfilters = [ "category = '%s'" % cls.category ]

        for k, v in filters:
            if v:
                qfilters.append('%s IN ' % k + cls.sql_filter_list(v))

        oattrs = ', '.join(esc(f[0]) for f in filters)
        fattrs = ', '.join(esc(a) for a in attrs)
        qfilters = ' AND '.join(qfilters)
        alimit = limit * len(cls.fields)

        for row in do("""
            SELECT %s FROM `%s` WHERE %s ORDER BY %s LIMIT %d 
        """ % (fattrs, table, qfilters, oattrs, alimit)):
            yield row

    @classmethod
    def load_from_table(cls, attrs, filters, table, limit, nkey=-2):
        result = {}
        fields = set(cls.fields)

        for row in cls.query_for(attrs, filters, table, limit):
            attr, value = row[nkey:]
            key = tuple(row[:nkey])

            if attr in fields:
                obj = result.get(key, None)

                if obj is None:
                    obj = cls()

                    for f in obj.fields:
                        setattr(obj, f, "")

                    for f, v in izip(attrs, key):
                        setattr(obj, f, v)

                    result[key] = obj

                setattr(obj, attr, value)

        return result.values()

    @classmethod
    def load(cls, names = None, limit = 10000):
        attrs = [ "name", "attr", "value" ]
        filters = [ ("name", names) ]
        table = "web_attributes"
        itr = cls.load_from_table(attrs, filters, table, limit)
        return sorted(itr, key = lambda x: x.name)

    @classmethod
    def load_all(cls):
        return cls.load()

    @classmethod
    def make_table(cls, objs, limit = 10000):
        cats = set()
        clss = set(type(o) for o in objs)
        fields = set.intersection(*[ set(c.fields) for c in clss ])
        ofields = []

        if len(clss) == 1:
            fields.remove('category')

        for c in clss:
            for f in c.fields:
                if f in fields and f not in ofields:
                    ofields.append(f)

        header = ''.join('<th>%s</th>' % f for f in ofields)
        rows = [ '<table class="table">\n<tr>%s</tr>' % str(header) ]

        for obj in objs:
            row = []

            for f in ofields:
                v = unicode(getattr(obj, f, ""))[:limit]
                if len(v) == limit: v = v[:limit-3] + '...'
                row.append('<td>%s</td>' % v.encode('utf-8'))

            rows.append('<tr>%s</tr>' % ''.join(row))

        rows.append('</table>')
        return '\n'.join(rows)

    @classmethod
    def iter_attrs(cls):
        for field in cls.fields:
            if field not in cls.indexes:
                yield field

    @classmethod
    def iter_rows(cls, objs, fields = (), limit = 10000):
        for obj in objs:
            row = []

            for f in fields:
                v = ""

                if f in cls.fields:
                    v = unicode(getattr(obj, f, ""))[:limit]

                if f in obj.extra_fields:
                    v = unicode(getattr(obj, f, ""))[:limit]

                if len(v) == limit: 
                    v = v[:limit-3] + '...'

                row.append(v.encode('utf-8'))

            yield row

    @classmethod
    def make_json(cls, objs, fields = (), limit = 10000):
        rows = list(cls.iter_rows(objs, fields = fields, limit = limit))
        return json.dumps({"data" : rows})

    def terse_row(self, limit = 20):
        row = []

        for attr in [ "name", "eventid" ]:
            if hasattr(self, attr):
                row = [ getattr(self, attr) ]

        for f in self.fields[2:]:
            if "category" not in f:
                v = unicode(getattr(self, f))[:limit]
                if len(v) == limit:
                    v = v[:limit - 3].strip() + '...'
                row.append(v)

        return tuple(row)

    def __str__(self):
        return type(self).__name__ + unicode(self.terse_row()).encode('ascii', 'replace')

    def html_format_name(self, limit = 30):
        v = unicode(self.name).encode('utf-8')[:limit]
        if len(v) == limit: v = v[:limit-3] + '...'
    
    def make_insert_events(self):
        evid = "unsaved"
        dt = datetime.datetime.now()

        events = [ 
            TSTPEvent.create(
                eventid     = evid, 
                userid      = "odinlake", 
                entrytime   = dt, 
                action      = "insert", 
                category    = "event", 
                refcategory = self.category, 
                category1   = self.category, 
                name1       = self.name, 
                category2   = "", 
                name2       = "", 
                field       = attr, 
                oldvalue    = "", # no old value
                newvalue    = getattr(self, attr),
                eventstate  = "pending",
            ) for attr in self.iter_attrs()
        ]
        
        return events

    def make_edit_events(self, reference):
        if reference is None:
            return self.make_insert_events()
        
        evid = "unsaved"
        dt = datetime.datetime.now()
        events = []
        
        for attr in self.iter_attrs():
            newval = getattr(self, attr)
            oldval = getattr(reference, attr)
            
            if newval != oldval:
                events.append( 
                    TSTPEvent.create(
                        eventid     = evid, 
                        userid      = "odinlake", 
                        entrytime   = dt, 
                        action      = "edit", 
                        category    = "event", 
                        refcategory = self.category, 
                        category1   = self.category, 
                        name1       = self.name, 
                        category2   = "", 
                        name2       = "", 
                        field       = attr, 
                        oldvalue    = oldval,
                        newvalue    = newval,
                        eventstate  = "pending",
                    )
                )
        
        return events


##################################################################
##
## Represents a Connection between two objects.
##
##################################################################
class TSTPConnection(TSTPObject):
    category = "featureof"
    fields = (
        "category",
        "category1",
        "name1",
        "category2",
        "name2",
    )
    
    @classmethod
    def commit_updates(cls, updates):
        """
        Write multiple attribute updates for this class into the database
        without further ado. Dangerous.
        """
        chunksize = 10000
        attrfields = [
            "category",
            "category1",
            "name1",
            "category2",
            "name2",
            "attr",
            "value",
        ]
        fstr = ", ".join('`%s`' % s for s in attrfields)
        vstr = ", ".join("%s" for s in attrfields)

        for i in range(0, len(updates), chunksize):
            do("REPLACE INTO `web_connections` (%s) values (%s)" % (fstr, vstr), updates[i:i + chunksize])
        
    @classmethod
    def commit_edit_object(cls, events, updates):
        evfields = [
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
        fstr = ", ".join('`%s`' % s for s in evfields)
        vstr = ", ".join("%s" for s in evfields)
        do("REPLACE INTO `web_events` (%s) values (%s)" % (fstr, vstr), events)

        cls.commit_updates(updates)
        
    @classmethod
    def edit_object(cls, cat1, name1, cat2, name2, attrs, vals):
        events, updates = cls.propose_edit_object(cat1, name1, cat2, name2, attrs, vals)
        cls.commit_edit_object(events, updates)

    @classmethod
    def load(
        cls, 
        cat1s = None,
        name1s = None,
        cat2s = None,
        name2s = None,
        limit = 10000,
    ):
        attrs = [ "category1", "name1", "category2", "name2", "attr", "value" ]
        filters = [
            ("category1", cat1s),
            ("name1", name1s),
            ("category2", cat2s),
            ("name2", name2s),
        ]
        table = "web_connections"
        itr = cls.load_from_table(attrs, filters, table, limit)

        return sorted(itr, key = lambda x: (x.name1, x.name2))

    def make_insert_events(self):
        evid = "unsaved"
        dt = datetime.datetime.now()
        attrs = [ 'weight', 'motivation' ]

        events = [ 
            TSTPEvent.create(
                eventid     = evid, 
                userid      = "odinlake", 
                entrytime   = dt, 
                action      = "insert", 
                category    = "event", 
                refcategory = self.category, 
                category1   = self.category1, 
                name1       = self.name1, 
                category2   = self.category2, 
                name2       = self.name2, 
                field       = attr, 
                oldvalue    = "", # no old value
                newvalue    = getattr(self, attr),
                eventstate  = "pending",
            ) for attr in attrs
        ]
        
        return events

    def make_edit_event(self, attr, newvalue):
        evid = "unsaved"
        dt = datetime.datetime.now()
        
        event = TSTPEvent.create(
            eventid     = evid, 
            userid      = "odinlake", 
            entrytime   = dt, 
            action      = "edit", 
            category    = "event", 
            refcategory = self.category, 
            category1   = self.category1, 
            name1       = self.name1, 
            category2   = self.category2, 
            name2       = self.name2, 
            field       = attr, 
            oldvalue    = getattr(self, attr),
            newvalue    = newvalue,
            eventstate  = "pending",
        )
        
        return event


##################################################################
##
## Represents a Story.
##
##################################################################
class Story(TSTPObject):
    category = "story"
    collections = ""
    components = ""
    meta = ""
    fields = (
        "name",
        "category",
        "title",
        "date",
        "description",
        "collections",
        "components",
        "meta",
    )
    preforder = {
        "tos" : 1,
        "tas" : 2,
        "tng" : 3,
    }

    @classmethod
    def prefix_sort(cls, obj):
        pref = obj.name[:3]
        s = cls.preforder.get(pref, 99)
        return (s, obj.name)

    @classmethod
    def make_json(cls, objs, fields = (), limit = 10000):
        objs.sort(key = lambda x: cls.prefix_sort(x))
        rows = list(cls.iter_rows(objs, fields = fields, limit = limit))
        if "meta" in fields:
            idx = fields.index("meta")
            for ii, row in enumerate(rows):
                if row[idx]:
                    row[idx] = json.loads(row[idx])
        return json.dumps({"data" : rows})


##################################################################
##
## Represents a Theme.
##
##################################################################
class Theme(TSTPObject):
    category = "theme"
    meta = ""
    fields = (
        "name",
        "category",
        "description",
        "parents",
        "meta",
    )

    def list_parents(self):
        """
        Parse the "parents" field
        Returns:
        List of parent theme names.
        """
        print(self.parents)
        parents = [t.strip() for t in re.split("[,\n]", self.parents)]
        return [t for t in parents if t]

    @classmethod
    def make_json(cls, objs, fields = (), limit = 10000):
        rows = list(cls.iter_rows(objs, fields = fields, limit = limit))
        if "meta" in fields:
            idx = fields.index("meta")
            for ii, row in enumerate(rows):
                if row[idx]:
                    row[idx] = json.loads(row[idx])
        return json.dumps({"data" : rows})


##################################################################
##
## Represents a Theme in a Story.
##
##################################################################
class StoryTheme(TSTPConnection):
    fields = TSTPConnection.fields + (
        "weight",
        "motivation",
        "capacity",
    )

    @classmethod
    def create(cls, story, theme, weight, motivation, capacity):
        return super(StoryTheme, cls).create(
            category="featureof",
            category1="story",
            name1=story,
            category2="theme",
            name2=theme,
            weight=weight,
            motivation=motivation,
            capacity=capacity
        )
    
    @classmethod
    def load(
        cls, 
        name1s = None,
        name2s = None,
        limit = 10000,
    ):
        return super(StoryTheme, cls).load(
            "story", name1s, "theme", name2s, limit
        )


##################################################################
##
## Represents a change in the database or other event of note.
##
##################################################################
class TSTPEvent(TSTPObject):
    category = "event"
    fields = (
        "eventid",      # a unique identifier
        "userid",       # identify user
        "entrytime",    # time of entry
        "eventstate",   # pending/committed/reverted/...
        "action",       # insert/edit/delete/...
        "category",     # event
        "refcategory",  # identifies the TSTPObject type acted on
        "category1",    # subject category or category1
        "name1",        # subject name or name1
        "category2",    # subject category2 for TSTPConnection
        "name2",        # subject name2 for TSTPConnection
        "field",        # field changed
        "oldvalue",     # old value if any
        "newvalue",     # new value if any
    )

    @classmethod
    def load(
        cls, 
        cat1s = None,
        name1s = None,
        cat2s = None,
        name2s = None,
        limit = 10000,
    ):
        attrs = list(cls.fields)
        filters = [
            ("category1", cat1s),
            ("name1", name1s),
            ("category2", cat2s),
            ("name2", name2s),
        ]
        table = "web_events"
        itr = cls.load_from_table(attrs, filters, table, limit, nkey=1)

        return sorted(itr, key = lambda x: x.entrytime)

    @classmethod
    def load_from_table(cls, attrs, filters, table, limit, nkey=-2):
        result = {}
        fields = list(cls.fields)

        for row in cls.query_for(attrs, filters, table, limit):
            key = tuple(row[:nkey])
            obj = result.get(key, None) or cls()
            result[key] = obj

            for attr, val in izip(attrs, row):
                setattr(obj, attr, val)

        return result.values()

    @classmethod
    def commit_many(cls, events):
        """
        Commit a batch of unsaved events. This will update
        objects and insert events for the updates.
        """
        evidbase = "ev.%d-" % uuid("event")
        idx = 0
        catmap = {
            ('story', ''): Story,
            ('theme', ''): Theme,
            ('story', 'theme'): StoryTheme,
        }
        klassmap = { klass: set() for klass in catmap.values() }
        klassevmap = { klass: [] for klass in catmap.values() }
        objmap = {}

        #: find previous object names for all classes
        for event in events:
            klass = catmap[(event.category1, event.category2)]
            klassmap[klass].add((event.name1, event.name2))

        #: batch load objects for every class
        for klass, items in klassmap.items():
            if "name2" in klass.fields:
                name1s = set( x[0] for x in items )
                name2s = set( x[1] for x in items )
                for obj in klass.load(name1s, name2s):
                    objmap[(klass, obj.name1, obj.name2)] = obj
            elif "name" in klass.fields:
                name1s = set( x[0] for x in items )
                for obj in klass.load(name1s):
                    objmap[(klass, obj.name, None)] = obj
            else:
                raise ValueError("Unknown object type")

        #: fill in missing info on event: id and old-value
        for event in events:
            event.eventid = evidbase + str(idx)
            idx += 1
            klass = catmap[(event.category1, event.category2)]
            oldobject = objmap.get((klass, event.name1, event.name2), None)

            if oldobject:
                event.action = "edit"
                event.oldvalue = getattr(oldobject, event.field)
            else:
                event.action = "insert"
                event.oldvalue = ""

            klassevmap[klass].append(event)

        for klass, events in klassevmap.items():
            updates = []

            for event in events:
                if 'name2' in klass.fields:
                    updates.append([
                        event.refcategory,
                        event.category1,
                        event.name1,
                        event.category2,
                        event.name2,
                        event.field,
                        event.newvalue,
                    ])
                else:
                    updates.append([
                        event.category1,
                        event.name1,
                        event.field,
                        event.newvalue,
                    ])
    
            if events:
                cls.write_many(events)
                klass.commit_updates(updates)

    @classmethod
    def write_many(cls, events, chunksize=5000):
        """
        Write many events to db. 
        This will not affect any other objects.
        """
        evfields = [
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
        n = 0

        while n < len(events):
            evvalues = []
            
            for event in events[n:n+chunksize]:
                row = []
                for field in evfields:
                    row.append(getattr(event, field))
                evvalues.append(row)

            fstr = ", ".join('`%s`' % s for s in evfields)
            vstr = ", ".join("%s" for s in evfields)
            do("REPLACE INTO `web_events` (%s) values (%s)" % (fstr, vstr), evvalues)
            n += chunksize


############## HELPERS ###############

def test():
    stories = Story.load_all()

    for story in stories:
        print(unicode(story).encode("ascii", "ignore"))


if __name__ == '__main__':
    test()
