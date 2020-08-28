"""
Name:           test_formatting.py
Description:    The purpose of this file is to test formatting of the data in GIT before it is
                imported into the (MySQL) DB and becomes live. Tests should FAIL on serious
                problems in order to prevent bad data from going live on the web. The script
                should only use data from GIT (not DB or cached), normally obtained via:
                    lib.dataparse.read_stories_from_txt
                    lib.dataparse.read_themes_from_txt
                    lib.dataparse.read_storythemes_from_txt
"""
import log
from credentials import GIT_THEMING_PATH
import os
from collections import defaultdict
import sys
import lib.tests
import lib.files
import lib.dataparse


NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")
STATSLEVEL = 1


class Tests(object):
    def test_read_themes(self):
        """
        Check that all theme definitions can be read.
        """
        lu = defaultdict(list)
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
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
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$"):
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
        for path in lib.files.walk(NOTESPATH, r".*\.st\.txt$"):
            for st in lib.dataparse.read_storythemes_from_txt(path, verbose=True):
                lu[(st.name1, st.name2)].append(path)
        for name in lu:
            if len(lu[name]) > 1:
                log.debug("multiple story themes for '%s' in: %s" % (name, lu[name]))

    def test_field_references(self):
        """
        Check that the "references" field is reasonably correct on all defined themes.
        """
        faults = 0
        for path in lib.files.walk(NOTESPATH, r".*\.th\.txt$"):
            for th in lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False):
                for line in getattr(th, "examples", "").split("\n"):
                    line = line.strip()
                    if any(line.startswith(x) for x in ['http://', 'https://']):
                        if ' ' in line or line.endswith(","):
                            log.warn("Bad http reference line in '%s': %s", th.name, line)
                            faults += 1
        return "Found %s bad references" % faults if faults else None


def main():
    log.debug("START test_formatting")
    exitcode = lib.tests.run_data_tests(Tests())
    if exitcode != 0:
        log.error("some tests Failed, setting exit code %d" % exitcode)
        sys.exit(exitcode)



