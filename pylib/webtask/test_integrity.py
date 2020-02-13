import log
from credentials import GIT_THEMING_PATH
import os
import lib.files
import traceback
import lib.dataparse


NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")


class Tests(object):
    def test_read_themes(self):
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".th.txt"):
                _ = list(lib.dataparse.read_themes_from_txt(path, True))

    def test_read_stories(self):
        for path in lib.files.walk(NOTESPATH, r".*\.(st|th)\.txt$", 0):
            if path.endswith(".st.txt"):
                _ = list(lib.dataparse.read_stories_from_txt(path, True))

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
