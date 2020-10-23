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
        # ' Checkout LTO v0.3.2 for testing purposes.
        # ' It contains 2931 unique themes (hard coded below).
        basepath = GIT_THEMING_PATH_HIST
        os.chdir(basepath)
        repo = Repo(GIT_THEMING_PATH_HIST)
        version = repo.tags[7]
        expected_theme_count = 2931
        expected_timestamp = '2019-10-28 22:31:22 (UTC)'
        expected_commit_id = '56b4640d27b6f78478cd6aada1189add3480bf17'
        themeobjs_list, timestamp, commit_id = webtask.cache_themes.get_theme_objs(version, repo, basepath)
        self.assertEqual(len(themeobjs_list), expected_theme_count)
        self.assertEqual(timestamp, expected_timestamp)
        self.assertEqual(commit_id, expected_commit_id)

    def test_init_themes_list(self):
        basepath = GIT_THEMING_PATH_HIST
        themeobj_1 = webobject.Theme(
            name='zombie',
            description='a theme description',
            parents='living corpse',
            meta=json.dumps({'source': './a/path'}))
        themeobj_2 = webobject.Theme(
            name='AI rights',
            description='another theme description',
            parents='human rights issue',
            meta=json.dumps({'source': './another/path'}))
        themeobj_3 = webobject.Theme(
            name='a common enemy unites',
            description='yet another theme description',
            parents='human nature',
            meta=json.dumps({'source': './yet/another/path'}))
        themeobjs_list = [themeobj_1, themeobj_2, themeobj_3]
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
        theme_name = 'romantic love'
        theme_description = 'Featured is that peculiar sort of love between people so often associated with sexual attraction'
        theme_parents = 'love'
        theme_references = 'https://en.wikipedia.org/wiki/Romance_(love)'
        source_path = '/notes/themes/primary-themes.th.txt'
        raw_source_path = basepath + source_path
        theme_meta = json.dumps({'source': raw_source_path})
        test_themeobj = webobject.Theme(
            name=theme_name,
            description=theme_description,
            parents=theme_parents,
            references=theme_references,
            meta=theme_meta)
        theme_od = webtask.cache_themes.init_theme_od(test_themeobj, basepath)
        self.assertEqual(theme_od['name'], theme_name)
        self.assertEqual(type(theme_od['aliases']), list)
        self.assertEqual(theme_od['description'], theme_description)
        self.assertEqual(type(theme_od['notes']), list)
        self.assertEqual(theme_od['parents'][0], theme_parents)
        self.assertEqual(type(theme_od['references']), list)
        self.assertEqual(type(theme_od['examples']), list)
        self.assertEqual(type(theme_od['relatedthemes']), list)
        self.assertEqual(theme_od['source'], '.' + source_path)

    def test_main(self):
        webtask.cache_themes.main(dry_run=True)

def main():
    unittest.main(verbosity=2)

