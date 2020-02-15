import log
from credentials import GIT_THEMING_PATH
import os
import lib.files
import traceback
import lib.dataparse
from collections import defaultdict


NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")


class Tests(object):
    def test_read_themes(self):
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".th.txt"):
                for th in lib.dataparse.read_themes_from_txt(path, verbose=True):
                    lu[th.name].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple theme definitions for '%s' in: %s" % (name, lu[name]))

    def test_read_stories(self):
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".st.txt"):
                for st in lib.dataparse.read_stories_from_txt(path, verbose=True):
                    lu[st.name].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple story definitions for '%s' in: %s" % (name, lu[name]))

    def test_read_storythemes(self):
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".st.txt"):
                for st in lib.dataparse.read_storythemes_from_txt(path, verbose=True):
                    lu[(st.name1, st.name2)].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple story themes for '%s' in: %s" % (name, lu[name]))

    def test_theme_cycles(self):
        import networkx as nx  # may not be present in which case test simply fails
        graph = nx.DiGraph()
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".th.txt"):
                objs = list(lib.dataparse.read_themes_from_txt(path, False))
                for theme in objs:
                    for parent in theme.parents.split(","):
                        graph.add_edge(theme, parent.strip())
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            for cycle in cycles:
                log.debug("cycle: %s" % repr(cycle))
            return "found %d cycles" % len(cycles)


def main():
    log.debug("START test_integrity")
    tests = Tests()

    for name in dir(tests):
        if name.startswith("test_"):
            meth = getattr(tests, name)
            res = None
            log.debug("RUNNING %s..." % name)
            try:
                res = meth()
            except:
                log.debug("ERROR in %s!" % name)
                traceback.print_exc()
            if res:
                log.debug("FAIL in %s!" % name)
                log.debug(res)
            else:
                log.debug("SUCCESS")
