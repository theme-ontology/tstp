"""
Write LTO collections and metadata to a JSON file; one for each tagged version in the git
repository. An additional JSON file containing the LTO contents for the latest commit is also
generated.

    pyrun webtask.cache_collections (from inside the scripts directory)

"""

from __future__ import print_function
import os
from credentials import GIT_THEMING_PATH_HIST
from credentials import PUBLIC_DIR
import lib.commits
import lib.files
import lib.dataparse
from git import Repo
import json
import io
from collections import OrderedDict
import pytz
import lib.log

def init_metadata_od(version, timestamp, commit_id, collection_count):
    """
    Store LTO meta data in an ordered dictionary.
    Args:
        version: string
        timestamp: string
        commit_id: string
        collection_count: integer
    Returns: OrderedDict
    """
    metadata_od = OrderedDict()
    metadata_od['version'] = version
    metadata_od['timestamp'] = timestamp
    metadata_od['git-commit-id'] = commit_id
    metadata_od['collection-count'] = collection_count
    return metadata_od

def get_story_objs(version, repo, basepath):
    """
    Store story metadata and thematic annotations for a given version of LTO in a big list.
    Args:
        version: string
        repo: git.repo.base.Repo
        basepath: string
    Returns: list, list, string, string
    """
    if version == 'dev':
        repo.git.pull('origin', 'master')
    else:
        repo.git.checkout(version)
    timestamp = repo.head.object.committed_datetime.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S (UTC)')
    commit_id = str(repo.head.object.hexsha)
    storyobjs_list = list()
    storythemeobjs_list = list()

    #' avoid searching for story files recursively in the early LTO versions
    #' doing so will lead to an error because of the presence of the testing file notes/mikael.onsjoe/test.st.txt
    levels = 0 if version == 'v0.1.2' or version == 'v0.1.3' or version == 'v0.2.0' else -1

    for path in lib.files.walk(path=os.path.join(basepath, 'notes'), pattern='.*\.st\.txt$', levels=levels):
        storyobjs_list.extend(lib.dataparse.read_stories_from_txt(path, addextras=True))
        storythemeobjs_list.extend(lib.dataparse.read_storythemes_from_txt(path))

    return storyobjs_list, storythemeobjs_list, timestamp, commit_id

def init_story_od(storyobj, basepath):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Story.
    Args:
        storyobj: TSTPObject
        basepath: string
    Returns: OrderedDict
    """
    #' create list entries for Story objects not of the 'collection' variety only
    if storyobj.name.startswith('Collection:'):
        story_od = None
    else:
        fields = [
            'story-id',
            'collection-ids'
        ]
        story_od = OrderedDict()
        for field in fields:
            story_od[field] = []
        story_od['story-id'] = storyobj.name
        story_od['collection-ids'] = filter(None, storyobj.collections.split('\n'))

    return story_od

def init_collection_od(storyobj, basepath):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Story of the 'collection' variety.
    Args:
        storyobj: TSTPObject
        basepath: string
    Returns: OrderedDict
    """
    #' only create list entries for Story objects of the 'collection' variety
    if not storyobj.name.startswith('Collection:'):
        collection_od = None
    else:
        fields = [
            'collection-id',
            'title',
            'date',
            'genres',
            'description',
            'component-story-ids',
            'references',
            'source'
        ]
        collection_od = OrderedDict()
        for field in fields:
            collection_od[field] = []
        collection_od['collection-id'] = storyobj.name
        collection_od['title'] = storyobj.title
        collection_od['date'] = storyobj.date
        collection_od['description'] = storyobj.description.rstrip().split('\n\n\n')[0]
        collection_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(storyobj.meta)['source'])
        collection_od['themes'] = []
        extra_fields = set(storyobj.extra_fields)
        if 'genre' in extra_fields:
            collection_od['genres'] = filter(None, [genre.strip() for genre in storyobj.genre.split(',')])
        if 'references' in extra_fields:
            collection_od['references'] = filter(None, storyobj.references.split('\n'))

    return collection_od

def init_stories_list(storyobjs_list, basepath):
    """
    Create a list of stories, where each story is represented by an ordered dictionary, for a given
    version of the repository.
    Args:
        storyobjs_list: list
        basepath: string
    Returns: list
    """
    # ' create ordered dictionary entry for each story in list
    stories_list = list()
    for storyobj in storyobjs_list:
        if not storyobj.name.startswith('Collection:'):
            story_od = init_story_od(storyobj, basepath)
            stories_list.append(story_od)

    return stories_list

def init_collections_list(storyobjs_list, basepath):
    """
    Create a list of collections, where each collection is represented by an ordered dictionary.
    Args:
        storyobjs_list: list
        basepath: string
    Returns: list
    """
    # ' create ordered dictionary entry for each story in list
    collections_list = list()
    for storyobj in storyobjs_list:
        if storyobj.name.startswith('Collection:'):
            collection_od = init_collection_od(storyobj, basepath)
            collections_list.append(collection_od)

    # ' sort collections in alphabetical order of collection title
    collections_list = sorted(collections_list, key=lambda i: i['title'])

    return collections_list

def populate_collections_with_component_stories_1(collections_list, storyobjs_list):
    """
    Add component stories to any collections defined directly in ./notes/collections/ folder files.
    Args:
        collections_list: list
        storyobjs_list: list
    Returns: list
    """
    collection_ids = [collection_od['collection-id'] for i, collection_od in enumerate(collections_list)]

    for storyobj in storyobjs_list:
        if storyobj.name.startswith('Collection:'):
            collection_id = storyobj.name
            component_story_names = filter(None, storyobj.components.split('\n'))
            for component_story_name in component_story_names:
                if collection_id in collection_ids:
                    collections_list[collection_ids.index(collection_id)]['component-story-ids'].append(component_story_name)

    return collections_list

def populate_collections_with_component_stories_2(collections_list, storyobjs_list):
    """
    Add component stories to any collections defined directly in ./notes/stories/*/ folder files.
    Args:
        collections_list: list
        storyobjs_list: list
    Returns: list
    """
    collection_ids = [collection_od['collection-id'] for i, collection_od in enumerate(collections_list)]

    for storyobj in storyobjs_list:
        if not storyobj.name.startswith('Collection:'):
            story_id = storyobj.name
            story_collection_ids = filter(None, storyobj.collections.split('\n'))
            for story_collection_id in story_collection_ids:
                if story_collection_id in collection_ids:
                    collections_list[collection_ids.index(story_collection_id)]['component-story-ids'].append(story_id)

    return collections_list

def populate_collections_with_themes(collections_list, storythemeobjs_list):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Theme.
    Args:
        collections_list: list
        storythemeobjs_list: list
    Returns: list
    """
    collection_ids = [collection_od['collection-id'] for i, collection_od in enumerate(collections_list)]

    for storythemeobj in storythemeobjs_list:
        if storythemeobj.name1.startswith('Collection:') and storythemeobj.name1 in collection_ids:
            thematic_annotation_od = init_thematic_annotation_od(storythemeobj)
            collections_list[collection_ids.index(storythemeobj.name1)]['themes'].append(thematic_annotation_od)

    return collections_list

def init_thematic_annotation_od(storythemeobj):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category StoryTheme.
    Args:
        storythemeobj: TSTPObject
    Returns: OrderedDict
    """
    fields = [
        'name',
        'level',
        'motivation'
    ]
    thematic_annotation_od = OrderedDict()
    for field in fields:
        thematic_annotation_od[field] = []
    thematic_annotation_od['name'] = storythemeobj.name2
    thematic_annotation_od['level'] = storythemeobj.weight
    thematic_annotation_od['motivation'] = storythemeobj.motivation
    return thematic_annotation_od

def write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=False):
    """
    Write LTO information to JSON file. Set 'overwrite' to 'True' to regenerate a non-developmental
    version file.
    Args:
        lto_json: unicode
        version: string
        overwrite: boolean
    """
    path = output_dir + '/' + 'lto-' + version + '-collections.json'
    if not os.path.exists(path) or overwrite:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(lto_json)

def main(dry_run=False):
    #' preliminaries
    basepath = GIT_THEMING_PATH_HIST
    output_dir = os.path.join(PUBLIC_DIR, 'data')
    lib.files.mkdirs(output_dir)
    os.chdir(basepath)

    #' setup git repository
    repo = Repo(GIT_THEMING_PATH_HIST)
    #' The first two versions (i.e. v0.1.0 and v0.1.1) are skipped on account that neither contains
    #' any themes. The tags exist for historical reasons that are uminportant here.
    versions = repo.tags[2:]
    versions = [str(version) for version in versions]
    versions.append('dev')

    if dry_run:
        versions = [str(repo.tags[7])]

    #' create a JSON file for each named version of LTO catalogued in the repository
    for version in versions:
        #' create ordered dictionary consisting of 1) LTO metadata and 2) a list of collections
        #' complete with component story ids
        lib.log.info("Processing LTO %s collections...", version)
        storyobjs_list, storythemeobjs_list, timestamp, commit_id = get_story_objs(version, repo, basepath)

        #' gather up all the story objects of the 'collection' variety into a list
        collections_list = init_collections_list(storyobjs_list, basepath)

        #' populate collections with component stories and collection level themes
        collections_list = populate_collections_with_component_stories_1(collections_list, storyobjs_list)
        collections_list = populate_collections_with_component_stories_2(collections_list, storyobjs_list)
        collections_list = populate_collections_with_themes(collections_list, storythemeobjs_list)

        # ' prepare LTO metadata to be written to JSON file
        metadata_od = init_metadata_od(version, timestamp, commit_id, collection_count=len(collections_list))

        # ' store LTO collections and metadata in an ordered dictionary
        lto_od = OrderedDict()
        lto_od['lto'] = metadata_od
        lto_od['collections'] = collections_list

        # ' convert LTO ordered dictionary to JSON format
        lto_json = json.dumps(lto_od, ensure_ascii=False, indent=4)

        #' write LTO JSON object to file
        #' set overwrite to True to force existing files to be overwritten
        #' only the developmental version should be written to file by default
        if not dry_run:
            if version == 'dev':
                write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=True)
            else:
                write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=False)
