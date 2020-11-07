"""
Name:           tests/webtask/cache_data.py
Description:    The purpose of this file is to test that the functions for preparing theme, story,
                and collection data to be written to file in JSON format are in good working order.
"""
from credentials import GIT_THEMING_PATH_HIST
import os
import webtask.cache_data
import unittest
import webobject
import json
from collections import OrderedDict

class TestCacheData(unittest.TestCase):
    def test_get_lto_data(self):
        #' Checkout LTO v0.3.2 for testing purposes.
        #' It contains 2931 unique themes, 2068 unique stories with 25728 thematic annotations
        #' (hard coded below).
        basepath = GIT_THEMING_PATH_HIST
        os.chdir(basepath)
        version = 'v0.3.2'
        #subprocess.check_output('git reset --hard origin/master'.split(), stderr=subprocess.STDOUT)
        #subprocess.check_output('git checkout tags/v0.3.2'.split(), stderr=subprocess.STDOUT)
        expected_theme_count = 2931
        expected_story_count = 2068
        expected_thematic_annotation_count = 25728
        expected_timestamp = '2019-10-28 22:31:22 (UTC)'
        expected_commit_id = '56b4640d27b6f78478cd6aada1189add3480bf17'
        themeobjs_list, storyobjs_list, storythemeobjs_list, timestamp, commit_id = webtask.cache_data.get_lto_data(version, basepath)
        self.assertEqual(len(themeobjs_list), expected_theme_count)
        self.assertEqual(len(storyobjs_list), expected_story_count)
        self.assertEqual(len(storythemeobjs_list), expected_thematic_annotation_count)
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
        themes_list = webtask.cache_data.init_themes_list(themeobjs_list, basepath)
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
        theme_od = webtask.cache_data.init_theme_od(test_themeobj, basepath)
        self.assertEqual(theme_od['name'], theme_name)
        self.assertEqual(type(theme_od['aliases']), list)
        self.assertEqual(theme_od['description'], theme_description)
        self.assertEqual(type(theme_od['notes']), list)
        self.assertEqual(theme_od['parents'][0], theme_parents)
        self.assertEqual(type(theme_od['references']), list)
        self.assertEqual(type(theme_od['examples']), list)
        self.assertEqual(type(theme_od['relatedthemes']), list)
        self.assertEqual(theme_od['source'], '.' + source_path)

    def test_init_stories_list(self):
        basepath = GIT_THEMING_PATH_HIST

        #' initialize three Story objects for testing purposes
        storyobj_1 = webobject.Story(
            name='movie: Robot Monster (1953)',
            title='Robot Monster',
            date='1953-06-24',
            description='A classic film.',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_2 = webobject.Story(
            name='movie: The Wizard of Oz (1939)',
            title='The Wizard of Oz',
            date='1939-08-25',
            description='Another classic film.',
            meta=json.dumps({'source': './another/token/path'}))
        storyobj_3 = webobject.Story(
            name='movie: A Trip to the Moon (1902)',
            title='A Trip to the Moon',
            date='1902-10-04',
            description='Yet another classic film.',
            meta=json.dumps({'source': './yet/another/token/path'}))
        storyobjs_list = [storyobj_1, storyobj_2, storyobj_3]

        #' test that correct number of stories are returned
        expected_story_count = len(storyobjs_list)
        stories_list = webtask.cache_data.init_stories_list(storyobjs_list, basepath)
        self.assertEqual(len(stories_list), expected_story_count)

        # test that stories are sorted in increasing order of release data
        expected_first_story_id = storyobj_3.name
        expected_second_story_id = storyobj_2.name
        expected_third_story_id = storyobj_1.name
        self.assertEqual(stories_list[0]['story-id'], expected_first_story_id)
        self.assertEqual(stories_list[1]['story-id'], expected_second_story_id)
        self.assertEqual(stories_list[2]['story-id'], expected_third_story_id)

    def test_init_story_od(self):
        basepath = GIT_THEMING_PATH_HIST

        #' test that collection entries not processed as stories
        storyobj = webobject.Story(
            name='Collection: a token collection',
            title='a token collection',
            date='2020-09-22',
            description='a description',
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_data.init_story_od(storyobj, basepath)
        self.assertEqual(story_od, None)

        #' test that any trailing reference information is correctly stripped from description text
        expected_description = 'A classic film.'
        storyobj = webobject.Story(
            name='movie: Robot Monster (1953)',
            title='Robot Monster',
            date='1953-06-24',
            description='A classic film.\n\n\nReferences: a reference',
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_data.init_story_od(storyobj, basepath)
        self.assertEqual(story_od['description'], expected_description)

        #' test that stories with multiple genres are correctly handled
        expected_genres = ['sci-fi', 'horror']
        storyobj = webobject.Story(
            name='movie: Robot Monster (1953)',
            title='Robot Monster',
            date='1953-06-24',
            genre='sci-fi, horror',
            description='A classic film.',
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_data.init_story_od(storyobj, basepath)
        self.assertEqual(story_od['genres'], expected_genres)

        #' test that multiple references are correctly handled
        reference_1 = 'a reference'
        reference_2 = 'another reference'
        expected_references = [reference_1, reference_2]
        storyobj = webobject.Story(
            name='movie: Robot Monster (1953)',
            title='Robot Monster',
            date='1953-06-24',
            description='A classic film.',
            references=reference_1 + '\n' + reference_2,
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_data.init_story_od(storyobj, basepath)
        self.assertEqual(story_od['references'], expected_references)

        #' test the story source path is correctly handled
        source_path_fragment = '/notes/stories/film/film-scifi-1950s.st.txt'
        expected_source_path = '.' + source_path_fragment
        storyobj = webobject.Story(
            name='movie: Robot Monster (1953)',
            title='Robot Monster',
            date='1953-06-24',
            description='A classic film.',
            meta=json.dumps({'source': basepath + source_path_fragment}))
        story_od = webtask.cache_data.init_story_od(storyobj, basepath)
        self.assertEqual(story_od['source'], expected_source_path)

    def test_init_thematic_annotation_od(self):
        #' test to confirm that a StoryTheme object is correctly converted into an orderdict entry
        storythemeobj = webobject.StoryTheme(
            name1='story id',
            name2='the desire for vengeance',
            weight='major',
            motivation='So-and-so sought to make so-and-so pay for this or that.')
        storytheme_od = webtask.cache_data.init_thematic_annotation_od(storythemeobj)
        self.assertEqual(storytheme_od.items()[0], ('name', storythemeobj.name2))
        self.assertEqual(storytheme_od.items()[1], ('level', storythemeobj.weight))
        self.assertEqual(storytheme_od.items()[2], ('motivation', storythemeobj.motivation))

    def test_populate_stories_with_themes(self):
        #' initialize a list of story OrderedDict objects
        story_ids = [
            'movie: A Trip to the Moon (1902)',
            'movie: The Wizard of Oz (1939)',
            'movie: Robot Monster (1953)']
        story_titles = [
            'A Trip to the Moon (1902)',
            'The Wizard of Oz (1939)',
            'Robot Monster (1953)']
        story_dates = ['1902-10-04', '1939-08-25', '1953-06-24']
        story_description = 'A classic film.'
        source_path = json.dumps({'source': './a/token/path'})
        story_od_1 = OrderedDict()
        story_od_1['story-id'] = story_ids[0]
        story_od_1['title'] = story_titles[0]
        story_od_1['date'] = story_dates[0]
        story_od_2 = OrderedDict()
        story_od_2['story-id'] = story_ids[1]
        story_od_2['title'] = story_titles[1]
        story_od_2['date'] = story_dates[1]
        story_od_3 = OrderedDict()
        story_od_3['story-id'] = story_ids[2]
        story_od_3['title'] = story_titles[2]
        story_od_3['date'] = story_dates[2]
        story_od_1['description'] = story_od_2['description'] = story_od_3['description'] = story_description
        story_od_1['source'] = story_od_2['source'] = story_od_3['source'] = source_path
        story_od_1['themes'] = story_od_2['themes'] = story_od_3['themes'] = []
        stories_list = [story_od_1, story_od_2, story_od_3]

        #' initialize a list of StoryTheme objects
        storythemeobj_1 = webobject.StoryTheme(
            name1='movie: Robot Monster (1953)',
            name2='the desire for vengeance',
            weight='major',
            motivation='So-and-so sought to make so-and-so pay for this or that.')
        storythemeobj_2 = webobject.StoryTheme(
            name1='movie: The Wizard of Oz (1939)',
            name2='romantic love',
            weight='minor',
            motivation='So-and-so was besotted with so-and-so.')
        storythemeobjs_list = [storythemeobj_1, storythemeobj_2]

        #' test thematically annotate Robot Monster (1953) with "the desire for vengeance"
        updated_stories_list = webtask.cache_data.populate_stories_with_themes(stories_list, storythemeobjs_list)
        self.assertEqual(updated_stories_list[2]['themes'][0]['name'], storythemeobj_1.name2)
        self.assertEqual(updated_stories_list[2]['themes'][0]['level'], storythemeobj_1.weight)
        self.assertEqual(updated_stories_list[2]['themes'][0]['motivation'], storythemeobj_1.motivation)

    def test_populate_stories_with_collection_info(self):
        # ' initialize a collection object and put it in a list
        component_story_names = [
            'movie: Alien (1979)',
            'movie: Aliens (1986)',
            'movie: Alien 3 (1992)',
            'movie: Alien Resurrection (1997)',
            'movie: Prometheus (2012)',
            'movie: Alien: Covenant (2017)']
        storyobj = webobject.Story(
            name='Collection: Alien',
            title='Alien',
            date='1979-2017',
            description='A classic film franchise.',
            components='\n'.join(component_story_names),
            meta=json.dumps({'source': './a/token/path'}))
        storyobjs_list = [storyobj]

        #' initialize a story OrderedDict object and put it in a list
        story_od = OrderedDict()
        story_od['story-id'] = 'movie: Alien (1979)'
        story_od['title'] = 'Alien'
        story_od['date'] = '1979-05-25'
        story_od['description'] = 'A classic film.'
        story_od['source'] = json.dumps({'source': './a/token/path'})
        story_od['collections'] = []
        stories_list = [story_od]

        #' test that collection info is correctly added to story entry
        expected_collections = ['Collection: Alien']
        expected_collection_count = len(expected_collections)
        updated_stories_list = webtask.cache_data.populate_stories_with_collection_info(storyobjs_list, stories_list)
        self.assertEqual(len(updated_stories_list[0]['collections']), expected_collection_count)
        self.assertEqual(updated_stories_list[0]['collections'], expected_collections)

    def test_main(self):
        webtask.cache_data.main(test_run=True)

def main():
    unittest.main(verbosity=2)

