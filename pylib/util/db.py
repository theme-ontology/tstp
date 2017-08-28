import sys
import dbdefine
import lib.files
import lib.dataparse
import log
from collections import defaultdict
from webobject import TSTPEvent


def main():
    args = sys.argv
    fromidx = args.index("util.db") + 1
    args = args[fromidx:]
    nargs = len(args)

    if args[0] == "clear":
        if raw_input("Clear Database? (yes/no) ") == "yes":
            dbdefine.create_tables(True)

    elif args[0] == "import":
        themes = defaultdict(list)
        stories = defaultdict(list)
        storythemes = defaultdict(list)

        for path in lib.files.walk(args[1], ".*\.(st|th)\.txt$", 0):
            log.info("READING: %s", path)

            if path.endswith(".th.txt"):
                objs = list(lib.dataparse.read_themes_from_txt(path, False))
                themes[path].extend(objs)
                log.info(".. found %d well defined themes", len(objs))

            if path.endswith(".st.txt"):
                objs1 = list(lib.dataparse.read_stories_from_txt(path, False))
                stories[path].extend(objs1)
                if objs1:
                    log.info(".. found %d well defined stories", len(objs1))
                objs2 = list(lib.dataparse.read_storythemes_from_txt(path, False))
                storythemes[path].extend(objs2)
                if objs2:
                    log.info(".. found %d themes in stories", len(objs2))
                if not objs1 and not objs2:
                    log.info(".. found nothing to take")

        rthemes = defaultdict(list)
        rstories = defaultdict(list)
        rstorythemes = defaultdict(list)
        rmatch = [ (themes, rthemes), (stories, rstories), (storythemes, rstorythemes) ]
        rorder = [ ("theme", rthemes), ("story", rstories), ("storytheme", rstorythemes) ]
        events = []

        for dd1, dd2 in rmatch:
            for path, ll in dd1.iteritems():
                for obj in ll:
                    if hasattr(obj, "name"):
                        dd2[obj.name].append((path, obj))
                    else:
                        dd2[(obj.name1, obj.name2)].append((path, obj))

        # drop story-themes for which either story or theme is not defined
        for story, theme in rstorythemes.keys():
            drop = False
            if theme not in rthemes:
                log.warn('Found undefined theme: "%s"...', theme)
                drop = True
            if story not in rstories:
                log.warn('Found undefined story: "%s"...', story)
                drop = True
            if drop:
                spec = [ path for path, _ in rstorythemes[(story, theme)] ]
                log.warn('Skipping "%s" found in: %s', (story, theme), spec)
                del rstorythemes[(story, theme)]

        # check for multiple definitions
        for thing, dd in rorder:
            for key, ll in dd.iteritems():
                if len(ll) > 1:
                    spec = [ path for path, _ in ll ]
                    log.warn('Multiple definitions of %s "%s": %s.', thing, key, spec)

        # note any parent-less themes
        for key, ll in rthemes.iteritems():
            for path, theme in ll:
                parents = filter(None, [ x.strip() for x in theme.parents.split(",") ])
                if not parents:
                    log.info('Top Level Theme "%s" in %s', key, path)
                elif key == "fictional gadget":
                    print theme, "::", theme.parents
                for parent in parents:
                    if parent not in rthemes:
                        log.info('Undefined parent theme "%s" for "%s" in %s', parent, key, path)

        # create and commit events
        for thing, dd in rorder:
            for key, ll in dd.iteritems():
                obj = ll[0][1]
                events.extend(obj.make_edit_events(None))

        log.info('Committing %d edit events...', len(events))
        log.set_level('WARN')
        #TSTPEvent.commit_many(events)





