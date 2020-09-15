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
import webobject
import webtask.cache_themes

NOTESPATH = os.path.join(GIT_THEMING_PATH, "notes")
STATSLEVEL = 1


class TestCacheThemes(unittest.TestCase):
    def setup(self):
        basepath = GIT_THEMING_PATH_HIST
        os.chdir(basepath)
        repo = Repo(GIT_THEMING_PATH_HIST)
        version = repo.versions[2]

    def test_get_theme_objs(self):
        themeobjs_list, timestamp, commit_id = get_theme_objs(self.version, self.repo, self.basepath)
        #lib.log.debug("read %s themes", len(themes))
        theme = themeobjs_list[0]
        self.assertEqual(len(themeobjs_list), 2075)
        #self.assertFalse(hasattr(theme, "unknown_field"))
        #self.assertEqual(theme.description.strip(), "stuff")
        #self.assertEqual(theme.parents.strip(), "more stuff")

    """
    def test_db(self):
        n = 5
        themes = list(lib.dataparse.read_themes_from_db(limit=n))[:n]
        lib.log.debug("read %s themes", len(themes))
        theme = themes[0]
        self.assertEqual(len(themes), n)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertTrue(hasattr(theme, "description"))
        self.assertTrue(hasattr(theme, "parents"))

    def is_timestamp(s):
        return re.fullmatch("^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] (UTC)$", s)

    def is_hex(s):
        return re.fullmatch(r"^[0-9a-fA-F]$", s or "") is not None
    """

def main():
    log.info("START cache_themes")
    unittest.main(verbosity=2)

#def main():
#    log.debug("START cache_themes")
#    exitcode = lib.tests.run_data_tests(TestCacheThemes())
#    if exitcode != 0:
#        log.error("some tests Failed, setting exit code %d" % exitcode)
#        sys.exit(exitcode)

