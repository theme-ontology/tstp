"""
Name:           tests/webtask/cache_themes.py
Description:    The purpose of this file is to test that the functions for preparing theme data to
                be written to file in JSON format are in good working order.
"""
from credentials import GIT_THEMING_PATH_HIST
import os
import webtask.cache_themes
import unittest
import webobject
import json
from git import Repo

class TestCacheThemes(unittest.TestCase):
    def test_get_theme_objs(self):
        # ' Checkout LTO v0.1.2 for testing purposes.
        # ' It contains 2074 unique themes (hard coded below).
        basepath = GIT_THEMING_PATH_HIST
        os.chdir(basepath)
        repo = Repo(GIT_THEMING_PATH_HIST)
        version = repo.tags[2]
        expected_theme_count = 2074
        themeobjs_list, timestamp, commit_id = webtask.cache_themes.get_theme_objs(version, repo, basepath)
        self.assertEqual(len(themeobjs_list), expected_theme_count)
        self.assertEqual(timestamp, '2017-12-11 20:57:55 (UTC)')
        self.assertEqual(commit_id, 'e968dba51c8e2f91cde7aefb6f66901b6f520553')

    def test_init_themes_list(self):
        basepath = GIT_THEMING_PATH_HIST
        test_themeobj_1 = webobject.Theme(name='zombie', description='a theme description', parents='living corpse', meta=json.dumps({'source': './a/path'}))
        test_themeobj_2 = webobject.Theme(name='AI rights', description='another theme description', parents='human rights issue', meta=json.dumps({'source': './another/path'}))
        test_themeobj_3 = webobject.Theme(name='a common enemy unites', description='yet another theme description', parents='human nature', meta=json.dumps({'source': './yet/another/path'}))
        themeobjs_list = [test_themeobj_1, test_themeobj_2, test_themeobj_3]
        expected_theme_count = len(themeobjs_list) + 1 # the three test themes plus the 'literary thematic entity' root theme
        themes_list = webtask.cache_themes.init_themes_list(themeobjs_list, basepath)
        self.assertEqual(len(themes_list), expected_theme_count)
        # ' If the alphabetical sorting by name works, then the first and last themes in the list of
        # ' themes will be named as follows:
        first_theme_name = 'a common enemy unites'
        last_theme_name = 'zombie'
        self.assertEqual(themes_list[0]['name'], first_theme_name)
        self.assertEqual(themes_list[-1]['name'], last_theme_name)

    def test_init_themes_od(self):
        basepath = GIT_THEMING_PATH_HIST
        test_theme_name = 'romantic love'
        test_theme_description = 'Featured is that peculiar sort of love between people so often associated with\nsexual attraction'
        test_theme_parents = 'love'
        test_theme_references = 'https://en.wikipedia.org/wiki/Romance_(love)'
        test_source_path = '/notes/themes/primary-themes.th.txt'
        raw_source_path = basepath + test_source_path
        test_theme_meta = json.dumps({'source': raw_source_path})
        test_themeobj = webobject.Theme(
            name=test_theme_name,
            description=test_theme_description,
            parents=test_theme_parents,
            references=test_theme_references,
            meta=test_theme_meta)
        theme_od = webtask.cache_themes.init_theme_od(test_themeobj, basepath)
        self.assertEqual(theme_od['name'], test_theme_name)
        self.assertEqual(type(theme_od['aliases']), list)
        self.assertEqual(theme_od['description'], test_theme_description)
        self.assertEqual(type(theme_od['notes']), list)
        self.assertEqual(theme_od['parents'][0], test_theme_parents)
        self.assertEqual(type(theme_od['references']), list)
        self.assertEqual(type(theme_od['examples']), list)
        self.assertEqual(type(theme_od['relatedthemes']), list)
        self.assertEqual(theme_od['source'], '.' + test_source_path)

def main():
    unittest.main(verbosity=2)




