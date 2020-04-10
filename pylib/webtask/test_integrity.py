import log
from credentials import GIT_THEMING_PATH
import os
import lib.files
import traceback
import lib.dataparse
from collections import defaultdict
import sys


NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")
STATSLEVEL = 1


class Tests(object):
    def test_read_themes(self):
        """
        Check that all theme definitions can be read.
        """
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$", 0):
            for th in lib.dataparse.read_themes_from_txt(path, verbose=True):
                lu[th.name].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple theme definitions for '%s' in: %s" % (name, lu[name]))

    def test_read_stories(self):
        """
        Check that all story definitions can be read.
        """
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$", 0):
            for st in lib.dataparse.read_stories_from_txt(path, verbose=True):
                lu[st.name].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple story definitions for '%s' in: %s" % (name, lu[name]))

    def test_read_storythemes(self):
        """
        Test that all themes as assigned to stories can be read from story files.
        """
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$", 0):
            for st in lib.dataparse.read_storythemes_from_txt(path, verbose=True):
                lu[(st.name1, st.name2)].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple story themes for '%s' in: %s" % (name, lu[name]))

    def test_theme_cycles(self):
        """
        Check that there are no circular theme definitions.
        """
        import networkx as nx  # may not be present in which case test simply fails
        graph = nx.DiGraph()
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$", 0):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            for theme in objs:
                for parent in theme.parents.split(","):
                    graph.add_edge(theme, parent.strip())
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            for cycle in cycles:
                log.debug("cycle: %s" % repr(cycle))
            return "found %d cycles" % len(cycles)

    def test_statistics(self):
        """
        Report a count of various objects defined.
        """
        def histogram(dd, refwidth=0, refval=0):
            vals = sorted(dd.items(), key=lambda x: -x[1])
            width = ((refwidth or max(len(k) for k in dd)) + 1) / 4 * 4 + 4
            barfactor = 60.0 / (refval or vals[0][1])
            patt = "%% %ds %%-7d" % width
            for key, val in vals:
                log.printfunc(patt % (key, val) + "*" * int(barfactor * (val + 0.5)))

        allfields = defaultdict(int)
        allstats = {}
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$", 0):
            objs = list(lib.dataparse.read_themes_from_txt(path, verbose=False))
            fields = defaultdict(int)
            for obj in objs:
                for attr in obj.fields + obj.extra_fields:
                    v = getattr(obj, attr, None)
                    if v:
                        fields[attr] += 1
                        allfields[attr] += 1
            allstats[path] = (fields,)
        refwidth = max(len(k) for k in allfields)
        refval = max(v for v in allfields.values())
        for path, (fields,) in allstats.items():
            log.debug("Stats for %s:", path[len(NOTESPATH):])
            histogram(fields, refwidth, refval)

        log.debug("Stats for ALL THEME files:")
        histogram(allfields, refwidth, refval)

        allfields = defaultdict(int)
        allstats = {}
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$", 0):
            objs = list(lib.dataparse.read_stories_from_txt(path, verbose=False, addextras=True))
            fields = defaultdict(int)
            for obj in objs:
                for attr in obj.fields + obj.extra_fields:
                    v = getattr(obj, attr, None)
                    if v:
                        fields[attr] += 1
                        allfields[attr] += 1
            allstats[path] = (fields,)
        refwidth = max(len(k) for k in allfields)
        refval = max(v for v in allfields.values())
        if STATSLEVEL >= 2:
            for path, (fields,) in allstats.items():
                log.debug("Stats for %s:", path[len(NOTESPATH):])
                histogram(fields, refwidth, refval)

        log.debug("Stats for ALL STORY files:")
        histogram(allfields, refwidth, refval)



def main():
    log.debug("START test_integrity")
    tests = Tests()
    exitcode = 0
    failedcount = 0
    successcount = 0

    for name in dir(tests):
        if name.startswith("test_"):
            meth = getattr(tests, name)
            res = None
            log.debug("RUNNING %s..." % name)
            try:
                res = meth()
            except:
                log.debug("ERROR in %s!" % name)
                exitcode = max(exitcode, 2)
                res = "test raised exception"
                traceback.print_exc()
            if res:
                log.debug("FAIL in %s!" % name)
                exitcode = max(exitcode, 1)
                failedcount += 1
                log.debug(res)
            else:
                log.debug("SUCCESS")
                successcount += 1

    log.debug("DONE Running tests. %d Failed, %d Succeeded." % (failedcount, successcount))

    if exitcode != 0:
        log.error("some tests Failed, setting exit code %d" % exitcode)
        sys.exit(exitcode)



