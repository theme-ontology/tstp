"""
Name:           test_integrity.py
Description:    The purpose of this file is to test the integrity of data in the (MySQL) DB
                after the data has been imported from GIT repository. It may also read from
                various cached resources that may have been refreshed.
"""
import log
from credentials import GIT_THEMING_PATH
import os
import lib.files
import traceback
import lib.dataparse
from collections import defaultdict
import sys
import lib.tests


NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")
STATSLEVEL = 1


class Tests(object):
    def test_theme_cycles(self):
        """
        Check that there are no circular theme definitions.
        """
        import networkx as nx  # may not be present in which case test simply fails
        graph = nx.DiGraph()
        selfrefs = []
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            for themeobj in objs:
                theme = themeobj.name
                for parent in themeobj.parents.split(","):
                    parent = parent.strip()
                    if theme == parent:
                        selfrefs.append(theme)
                    else:
                        graph.add_edge(theme, parent.strip())
        cycles = list(nx.simple_cycles(graph))
        for selfref in selfrefs:
            log.debug("Self-reference: %s" % repr(selfref))
        for cycle in cycles:
            log.debug("cycle: %s" % repr(cycle))
        if cycles or selfrefs:
            return "found %d cycles and %d self-parenting themes" % (len(cycles), len(selfrefs))

    def test_unused_themes(self):
        """
        List all unused themes that are defined, but do not fail.
        """
        counts = defaultdict(int)
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$"):
            for st in lib.dataparse.read_storythemes_from_txt(path, verbose=True):
                counts[st.name2] += 1
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            for theme in objs:
                for parent in theme.parents.split(","):
                    counts[parent.strip()] += 1
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            for theme in objs:
                if counts[theme.name] == 0:
                    log.warn("Found unused theme '%s' in: %s", theme.name, path)

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
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
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
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$"):
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
    exitcode = lib.tests.run_data_tests(Tests())
    if exitcode != 0:
        log.error("some tests Failed, setting exit code %d" % exitcode)
        sys.exit(exitcode)



