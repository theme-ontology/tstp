"""
Name:           test_cache_themes.py
Description:    The purpose of this file is to test that the functions for preparing theme data to
                be written to file in JSON format are in good working order.
"""
import log
from credentials import GIT_THEMING_PATH_HIST
import os
import webtask.cache_themes
import unittest
from git import Repo

NOTESPATH = os.path.join(GIT_THEMING_PATH_HIST, "notes")
STATSLEVEL = 1

class TestCacheThemes(unittest.TestCase):
    def setUp(self):
        #' Checkout LTO v0.1.2 for testing purposes.
        #' It contains 2074 unique themes (hard coded below).
        self.basepath = GIT_THEMING_PATH_HIST
        os.chdir(self.basepath)
        self.repo = Repo(GIT_THEMING_PATH_HIST)
        self.version = self.repo.tags[2]
        self.number_of_themes = 2074
        #' If the alphabetical sorting works, then the first and second last themes in the list of
        #' themes will be named as follows:
        self.first_theme = '2D beings'
        self.second_last_theme = 'zoo making alien race'

    def test_get_theme_objs(self):
        themeobjs_list, timestamp, commit_id = webtask.cache_themes.get_theme_objs(self.version, self.repo, self.basepath)
        #lib.log.debug("read %s themes", len(themeobjs_list))
        self.assertEqual(len(themeobjs_list), self.number_of_themes)
        self.assertEqual(timestamp, '2017-12-11 20:57:55 (UTC)')
        self.assertEqual(commit_id, 'e968dba51c8e2f91cde7aefb6f66901b6f520553')

    def test_init_themes_list(self):
        themeobjs_list = webtask.cache_themes.get_theme_objs(self.version, self.repo, self.basepath)[0]
        themes_list = webtask.cache_themes.init_themes_list(themeobjs_list, self.basepath)
        self.assertEqual(len(themes_list), self.number_of_themes + 1) #' The number of themes in v0.1.2 of the LTO plus the root theme "literary thematic entity" which is added manually.
        self.assertEqual(themes_list[0]['name'], self.first_theme)
        self.assertEqual(themes_list[-2]['name'], self.second_last_theme)

def main():
    unittest.main(verbosity=2)




