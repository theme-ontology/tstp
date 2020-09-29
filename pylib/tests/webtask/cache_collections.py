"""
Name:           tests/webtask/cache_collections.py
Description:    The purpose of this file is to test that the functions for preparing collection
                data to be written to file in JSON format are in good working order.
"""
from credentials import GIT_THEMING_PATH_HIST
import os
import webtask.cache_collections
import unittest
import webobject
import json
from git import Repo
from collections import OrderedDict

class TestCacheStories(unittest.TestCase):
    def test_get_story_objs(self):
        # ' verify that LTO v0.3.2 checks out correctly
        # ' it contains 2068 unique stories and 25728 thematic annotations (hard coded below)
        basepath = GIT_THEMING_PATH_HIST
        os.chdir(basepath)
        repo = Repo(GIT_THEMING_PATH_HIST)
        version = repo.tags[7]
        expected_story_count = 2068
        expected_thematic_annotation_count = 25728
        expected_timestamp = '2019-10-28 22:31:22 (UTC)'
        expected_commit_id = '56b4640d27b6f78478cd6aada1189add3480bf17'
        storyobjs_list, storythemeobjs_list, timestamp, commit_id = webtask.cache_collections.get_story_objs(version, repo, basepath)
        self.assertEqual(len(storyobjs_list), expected_story_count)
        self.assertEqual(len(storythemeobjs_list), expected_thematic_annotation_count)
        self.assertEqual(timestamp, expected_timestamp)
        self.assertEqual(commit_id, expected_commit_id)

    def test_init_stories_list(self):
        basepath = GIT_THEMING_PATH_HIST

        #' initialize three Story objects for testing purposes
        expected_story_count = 1
        expected_story_id = 'movie: A Trip to the Moon (1902)'
        storyobj = webobject.Story(
            name='movie: A Trip to the Moon (1902)',
            title='A Trip to the Moon',
            date='1902-10-04',
            description='A classic film.',
            meta=json.dumps({'source': './yet/another/token/path'}))
        storyobjs_list = [storyobj]

        #' test the correct story info is returned
        expected_story_count = len(storyobjs_list)
        stories_list = webtask.cache_collections.init_stories_list(storyobjs_list, basepath)
        self.assertEqual(len(stories_list), expected_story_count)
        self.assertEqual(stories_list[0]['story-id'], expected_story_id)

    def test_init_story_od(self):
        basepath = GIT_THEMING_PATH_HIST

        #' test that collection entries not processed as stories
        storyobj = webobject.Story(
            name='Collection: Akira Kurosawa',
            title='Akira Kurosawa',
            date='1949-1985',
            description='Films written or directed by Akira Kurosawa.',
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_collections.init_story_od(storyobj, basepath)
        self.assertEqual(story_od, None)

        # ' test that multiple collection stories are correctly handled
        collection_ids = [
            'Collection: Science fiction films of the 1980s',
            'Collection: The Terminator']
        storyobj = webobject.Story(
            name='movie: The Terminator (1984)',
            title='The Terminator',
            date='1984-10-26',
            description='A classic film.',
            collections='\n'.join(collection_ids),
            meta=json.dumps({'source': './a/token/path'}))
        story_od = webtask.cache_collections.init_story_od(storyobj, basepath)
        self.assertEqual(story_od['story-id'], storyobj.name)
        self.assertEqual(story_od['collection-ids'], collection_ids)

    def test_init_collection_od(self):
        basepath = GIT_THEMING_PATH_HIST

        #' test that non-collection entries not processed as collections
        storyobj = webobject.Story(
            name='movie: A Trip to the Moon (1902)',
            title='A Trip to the Moon',
            date='2020-09-22',
            description='A classic film.',
            meta=json.dumps({'source': './a/token/path'}))
        collection_od = webtask.cache_collections.init_collection_od(storyobj, basepath)
        self.assertEqual(collection_od, None)

        #' test that collection entries correctly handled
        storyobj = webobject.Story(
            name='Collection: Akira Kurosawa',
            title='Akira Kurosawa',
            date='1949-1985',
            description='Films written or directed by Akira Kurosawa.',
            meta=json.dumps({'source': './a/token/path'}))
        collection_od = webtask.cache_collections.init_collection_od(storyobj, basepath)
        self.assertEqual(collection_od['collection-id'], storyobj.name)
        self.assertEqual(collection_od['title'], storyobj.title)
        self.assertEqual(collection_od['date'], storyobj.date)
        self.assertEqual(collection_od['genres'], [])
        self.assertEqual(collection_od['description'], storyobj.description)
        self.assertEqual(collection_od['references'], [])
        self.assertEqual(collection_od['component-story-ids'], [])

    def init_collections_list(self):
        basepath = GIT_THEMING_PATH_HIST

        #' initialize four Story objects for testing purposes: three of the collection variety and
        #' one of the story variety
        storyobj_1 = webobject.Story(
            name='Collection: William Shakespeare Plays',
            title='William Shakespeare Plays',
            date='1602-1606',
            description='Plays written by the English playwright, poet, and actor William Shakespeare.',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_2 = webobject.Story(
            name='movie: A Trip to the Moon (1902)',
            title='A Trip to the Moon',
            date='1902-10-04',
            description='A classic film',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_3 = webobject.Story(
            name='Collection: X-men',
            title='X-men',
            date='2000-2019',
            description='The X-Men is an American superhero film series.',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_4 = webobject.Story(
            name='Collection: Akira Kurosawa',
            title='Akira Kurosawa',
            date='1949-1985',
            description='Films written or directed by Akira Kurosawa.',
            meta=json.dumps({'source': './a/token/path'}))
        storyobjs_list = [storyobj_1, storyobj_2, storyobj_3, storyobj_4]

        #' test that correct number of collections is returned
        expected_story_count = len(storyobjs_list) - 1
        collections_list = webtask.cache_collections.init_collections_list(storyobjs_list, basepath)
        self.assertEqual(len(collections_list), expected_story_count)

        #' test that collections are alphabetically sorted by title
        expected_first_collection_id = storyobj_4.name
        expected_second_collection_id = storyobj_1.name
        expected_third_collection_id = storyobj_3.name
        self.assertEqual(collections_list[0]['collection-id'], expected_first_collection_id)
        self.assertEqual(collections_list[1]['collection-id'], expected_second_collection_id)
        self.assertEqual(collections_list[2]['collection-id'], expected_third_collection_id)

    def test_populate_collections_with_component_stories_1(self):
        #' initialize a list containing one collection OrderedDict object
        collection_od = OrderedDict()
        collection_od['collection-id'] = 'Collection: Akira Kurosawa'
        collection_od['title'] = 'Akira Kurosawa'
        collection_od['date'] = '1949-1985'
        collection_od['description'] = 'Films written or directed by Akira Kurosawa.'
        collection_od['component-story-ids'] = []
        collections_list = [collection_od]

        #' initialize a collection Story object
        expected_component_story_ids = [
            'movie: Dersu Uzala (1975)',
            'movie: High and Low (1963)',
            'movie: Ikiru (1952)',
            'movie: Ran (1985)',
            'movie: Rashomon (1950)',
            'movie: Red Beard (1965)',
            'movie: Sanjuro (1962)',
            'movie: Seven Samurai (1954)',
            'movie: Stray Dog (1949)',
            'movie: The Hidden Fortress (1958)',
            'movie: Throne of Blood (1957)',
            'movie: Yojimbo (1961)']
        storyobj = webobject.Story(
            name='Collection: Akira Kurosawa',
            title='Akira Kurosawa',
            date='1949-1985',
            description='Films written or directed by Akira Kurosawa.',
            collections='Collection: Akira Kurosawa',
            components='\n'.join(expected_component_story_ids),
            meta=json.dumps({'source': './a/token/path'}))
        storyobjs_list = [storyobj]

        #' test that the collection contains the expected component stories
        updated_collections_list = webtask.cache_collections.populate_collections_with_component_stories_1(collections_list, storyobjs_list)
        self.assertEqual(updated_collections_list[0]['component-story-ids'], expected_component_story_ids)

    def test_populate_collections_with_component_stories_2(self):
        #' initialize a list containing one collection OrderedDict object
        collection_od = OrderedDict()
        collection_od['collection-id'] = 'Collection: Akira Kurosawa'
        collection_od['title'] = 'Akira Kurosawa'
        collection_od['date'] = '1949-1985'
        collection_od['description'] = 'Films written or directed by Akira Kurosawa.'
        collection_od['component-story-ids'] = []
        collections_list = [collection_od]

        #' initialize list of three Story objects: two are component stories of the above defined
        # collection and one not
        storyobj_1 = webobject.Story(
            name='movie: Rashomon (1950)',
            title='Rashomon',
            date='1950-08-25',
            description='A classic film.',
            collections='Collection: Akira Kurosawa',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_2 = webobject.Story(
            name='movie: The Terminator (1984)',
            title='The Terminator',
            date='1984-10-26',
            description='A classic film.',
            collections='Collection: Science fiction films of the 1980s\nCollection: The Terminator',
            meta=json.dumps({'source': './a/token/path'}))
        storyobj_3 = webobject.Story(
            name='movie: Seven Samurai (1954)',
            title='Seven Samurai',
            date='1954-04-26',
            description='A classic film.',
            collections='Collection: Akira Kurosawa\nCollection: dummy collection',
            meta=json.dumps({'source': './a/token/path'}))
        storyobjs_list = [storyobj_1, storyobj_2, storyobj_3]

        #' test that the collection contains the expected component stories
        expected_component_story_ids = [
            'movie: Rashomon (1950)',
            'movie: Seven Samurai (1954)']
        updated_collections_list = webtask.cache_collections.populate_collections_with_component_stories_2(collections_list, storyobjs_list)
        self.assertEqual(updated_collections_list[0]['component-story-ids'], expected_component_story_ids)

    def test_populate_collections_with_themes(self):
        #' initialize a list of two collection OrderedDict objects
        collection_ids = [
            'Collection: Akira Kurosawa',
            'Collection: X-men']
        collection_titles = [
            'Akira Kurosawa',
            'X-men']
        collection_dates = ['1949-1985', '2000-2019']
        collection_descriptions = [
            'Films written or directed by Akira Kurosawa.',
            'The X-Men is an American superhero film series.']
        source_path = json.dumps({'source': './a/token/path'})
        collection_od_1 = OrderedDict()
        collection_od_1['collection-id'] = collection_ids[0]
        collection_od_1['title'] = collection_titles[0]
        collection_od_1['date'] = collection_dates[0]
        collection_od_1['description'] = collection_descriptions[0]
        collection_od_1['themes'] = []
        collection_od_2 = OrderedDict()
        collection_od_2['collection-id'] = collection_ids[1]
        collection_od_2['title'] = collection_titles[1]
        collection_od_2['date'] = collection_dates[1]
        collection_od_2['description'] = collection_descriptions[1]
        collection_od_2['themes'] = []
        collection_od_1['source'] = collection_od_2['source'] = source_path
        collections_list = [collection_od_1, collection_od_2]

        #' initialize a list of StoryTheme objects
        storythemeobj = webobject.StoryTheme(
            name1='Collection: X-men',
            name2='speculative ability',
            weight='major',
            motivation='Each X-man has a signature superpower.')
        storythemeobjs_list = [storythemeobj]

        #' test the X-men collection is thematically annotated with "speculative ability"
        expected_themes = ['speculative ability']
        updated_collections_list = webtask.cache_collections.populate_collections_with_themes(collections_list, storythemeobjs_list)
        #self.assertEqual(updated_collections_list[1]['themes'][0]['name'], storythemeobj.name2)
        self.assertEqual(updated_collections_list[1]['themes'][0]['name'], storythemeobj.name2)
        self.assertEqual(updated_collections_list[1]['themes'][0]['level'], storythemeobj.weight)
        self.assertEqual(updated_collections_list[1]['themes'][0]['motivation'], storythemeobj.motivation)

    def test_init_thematic_annotation_od(self):
        #' test to confirm that a StoryTheme object is correctly converted into an orderdict entry
        storythemeobj = webobject.StoryTheme(
            name1='story id',
            name2='the desire for vengeance',
            weight='major',
            motivation='So-and-so sought to make so-and-so pay for this or that.')
        storytheme_od = webtask.cache_collections.init_thematic_annotation_od(storythemeobj)
        self.assertEqual(storytheme_od.items()[0], ('name', storythemeobj.name2))
        self.assertEqual(storytheme_od.items()[1], ('level', storythemeobj.weight))
        self.assertEqual(storytheme_od.items()[2], ('motivation', storythemeobj.motivation))

    def test_main(self):
        webtask.cache_collections.main(dry_run=True)

def main():
    unittest.main(verbosity=2)
