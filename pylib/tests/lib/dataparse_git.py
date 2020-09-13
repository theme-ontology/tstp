import unittest
import os

import lib.dataparse
import lib.log
import logging
import credentials

logging.basicConfig(level = logging.DEBUG)
lib.log.printfunc = logging.debug


##
## This test uses data from GIT and may break if the git repo is reorganized
## (add tests sparingly)
##


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.voyager_path = os.path.join(
            credentials.GIT_THEMING_PATH, "notes", "stories", "television", "tv-startrek-voyager.st.txt")

    def test_voyager(self):
        stories = list(lib.dataparse.read_stories_from_txt(self.voyager_path))
        lib.log.debug("read %s stories  from %s", len(stories), self.voyager_path)


class TestThemes(unittest.TestCase):
    def setUp(self):
        self.theme_path = os.path.join(
            credentials.GIT_THEMING_PATH, "notes", "themes", "primary-themes.th.txt")

    def tearDown(self):
        pass

    def test_txt_expanded(self):
        themeobjs = list(lib.dataparse.read_themes_from_txt(self.theme_path, addextras=True, combinedescription=False))
        lib.log.debug("read %s themes", len(themeobjs))
        for themeobj in themeobjs[:2]:
            lib.log.debug("themeobj: %s", themeobj)
            lib.log.debug("theme.extra_fields: %s", themeobj.extra_fields)
            lib.log.debug("theme.description:\n%s", themeobj.description.strip())
            self.assertFalse(hasattr(themeobj, "unknown_field"))


def main():
    unittest.main(verbosity=2)

