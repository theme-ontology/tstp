"""
Write LTO data to a JSON files for each modern tagged version in the git repository. An
additional JSON file containing the LTO contents for the latest commit (i.e. the "dev" version) is
also generated.

    pyrun webtask.cache_data (from inside the scripts directory)

"""

from __future__ import print_function
import os
from credentials import GIT_THEMING_PATH_HIST
from credentials import PUBLIC_DIR
import lib.commits
import lib.files
import lib.dataparse
import lib.textformat
import json
import io
from collections import OrderedDict
import pytz
import lib.log
import subprocess
import dateutil.parser

def get_lto_data(version, basepath):
    """
    Return theme, story, collection, and metadata for a given LTO version.
    Args:
        version: string
        basepath: string
    Returns: list, list, list, string, string
    """

    #' these early versions require special handling as detailed below
    BROKEN_VERSIONS = ['v0.1.2', 'v0.1.3', 'v0.2.0', 'v0.3.0']

    #' checkout repository and store commit hash and commit timestamp
    if version == 'dev':
        subprocess.check_output("git reset --hard origin/master".split(), stderr=subprocess.STDOUT)
    else:
        command_str = "git checkout tags/" + version
        subprocess.check_output(command_str.split(), stderr=subprocess.STDOUT)
    commit_id = subprocess.check_output("git rev-parse HEAD".split()).decode("utf-8").rstrip()
    command_str = 'git show -s --format=%ci ' + commit_id
    timestamp_str = subprocess.check_output(command_str.split(), env=dict(os.environ, TZ="UTC")).decode("utf-8").rstrip()
    timestamp = dateutil.parser.parse(timestamp_str).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S (%Z)")

    #' store themes, stories, and story thematic annotations
    themeobjs_list = list()
    storyobjs_list = list()
    storythemeobjs_list = list()

    #' suppress warnings for stories with missing necessary fields in some older LTO versions
    broken = True if version in BROKEN_VERSIONS else False

    #' avoid searching for story files recursively in the early LTO versions
    #' doing so will lead to an error for v0.1.2, v0.1.3, and v0.2.0 because of the presence of the
    #' testing file notes/mikael.onsjoe/test.st.txt
    levels = 0 if version in BROKEN_VERSIONS else -1

    #' store theme data
    for path in lib.files.walk(os.path.join(basepath, 'notes'), '.*\.th\.txt$'):
        if broken:
            themeobjs_list.extend(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False, strict=False))
        else:
            themeobjs_list.extend(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))

    #' store story and story thematic annotation data (this includes collection data)
    for path in lib.files.walk(path=os.path.join(basepath, 'notes'), pattern='.*\.st\.txt$', levels=levels):
        if broken:
            storyobjs_list.extend(
                lib.dataparse.read_stories_from_txt(path, addextras=True, strict=False))
        else:
            storyobjs_list.extend(lib.dataparse.read_stories_from_txt(path, addextras=True))

        storythemeobjs_list.extend(lib.dataparse.read_storythemes_from_txt(path))

    return themeobjs_list, storyobjs_list, storythemeobjs_list, timestamp, commit_id

def init_metadata_od(version, timestamp, commit_id, category, count):
    """
    Store LTO meta data in an ordered dictionary.
    Args:
        category: string
        version: string
        timestamp: string
        commit_id: string
        count: integer
    Returns: OrderedDict
    """
    metadata_od = OrderedDict()
    metadata_od['version'] = version
    metadata_od['timestamp'] = timestamp
    metadata_od['git-commit-id'] = commit_id
    metadata_od['encoding'] = 'UTF-8'
    metadata_od[category + '-count'] = count
    return metadata_od

def init_theme_od(themeobj, basepath):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category theme.
    Args:
        themeobj: TSTPObject
        basepath: string
    Returns: OrderedDict
    """
    fields = [
        'name',
        'aliases',
        'description',
        'notes',
        'parents',
        'references',
        'examples',
        'relatedthemes',
        'source'
    ]
    theme_od = OrderedDict()
    for field in fields:
        theme_od[field] = []
    theme_od['name'] = themeobj.name
    theme_od['description'] = lib.textformat.remove_wordwrap(themeobj.description)
    if hasattr(themeobj, 'parents'):
        theme_od['parents'] = filter(None, [parent.strip() for parent in themeobj.parents.split(',')])
    if theme_od['parents'] == []:
        theme_od['parents'] = ['literary thematic entity']
    theme_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(themeobj.meta)['source'])
    extra_fields = set(themeobj.extra_fields)
    if 'aliases' in extra_fields:
        theme_od['aliases'] = filter(None, [alias.strip() for alias in themeobj.aliases.split(',')])
    if 'notes' in extra_fields:
        theme_od['notes'] = filter(None, lib.textformat.remove_wordwrap(themeobj.notes).split('\n\n'))
    if 'references' in extra_fields:
        theme_od['references'] = filter(None, themeobj.references.split('\n'))
    if 'examples' in extra_fields:
        theme_od['examples'] = filter(None, lib.textformat.remove_wordwrap(themeobj.examples).split('\n\n'))
    if 'relatedthemes' in extra_fields:
        theme_od['relatedthemes'] = filter(None, [relatedtheme.strip() for relatedtheme in themeobj.relatedthemes.split(',')])
    return theme_od

def init_story_od(storyobj, basepath):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Story.
    Args:
        storyobj: TSTPObject
        basepath: string
    Returns: OrderedDict
    """
    #' do not create list entries for collections
    if storyobj.name.startswith('Collection:'):
        story_od = None
    else:
        fields = [
            'story-id',
            'title',
            'date',
            'genres',
            'description',
            'collections',
            'references',
            'source',
            'themes'
        ]
        story_od = OrderedDict()
        for field in fields:
            story_od[field] = []
        story_od['story-id'] = storyobj.name
        if hasattr(storyobj, 'title'):
            story_od['title'] = storyobj.title
        else:
            story_od['title'] = ''
        if hasattr(storyobj, 'date'):
            story_od['date'] = storyobj.date
        else:
            story_od['date'] = ''
        #' the split on three newlines is needed to get rid of the story references which are
        #' included at the end of the description
        story_od['description'] = lib.textformat.remove_wordwrap(storyobj.description.rstrip().split('\n\n\n')[0])
        story_od['collections'] = filter(None, storyobj.collections.split('\n'))
        story_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(storyobj.meta)['source'])
        extra_fields = set(storyobj.extra_fields)
        if 'genre' in extra_fields:
            story_od['genres'] = filter(None, [genre.strip() for genre in storyobj.genre.split(',')])
        if 'references' in extra_fields:
            story_od['references'] = filter(None, storyobj.references.split('\n'))

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
        if hasattr(storyobj, 'title'):
            collection_od['title'] = storyobj.title
        else:
            collection_od['title'] = ''
        if hasattr(storyobj, 'date'):
            collection_od['date'] = storyobj.date
        else:
            collection_od['date'] = ''
        collection_od['description'] = lib.textformat.remove_wordwrap(storyobj.description.rstrip().split('\n\n\n')[0])
        collection_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(storyobj.meta)['source'])
        collection_od['themes'] = []
        extra_fields = set(storyobj.extra_fields)
        if 'genre' in extra_fields:
            collection_od['genres'] = filter(None, [genre.strip() for genre in storyobj.genre.split(',')])
        if 'references' in extra_fields:
            collection_od['references'] = filter(None, storyobj.references.split('\n'))

    return collection_od

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

def init_themes_list(themeobjs_list, basepath):
    """
    Create a list of themes, where each theme is represented by an ordered dictionary, for a given
    version of the repository. The list of themes is returned along with the timestamp and commit
    hash of the given version.
    Args:
        version: string
        basepath: string
    Returns: list
    """
    # ' read theme files
    themes_list = list()
    for themeobj in themeobjs_list:
        theme_od = init_theme_od(themeobj, basepath)
        themes_list.append(theme_od)

    # ' add literary thematic entity as root theme
    themes_list = add_root_theme(themes_list)

    # ' sort themes in alphabetical order of the 'name' field
    themes_list = sorted(themes_list, key=lambda i: i['name'].lower())

    return themes_list

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

    # ' sort stories by increasing order of release data
    stories_list = sorted(stories_list, key=lambda i: i['date'])

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

def add_root_theme(themes_list):
    """
    Add 'literary thematic entity' as root theme.
    Args:
        themes_list: list
    Returns: list
    """

    #' initialize ordered dict entry for 'literary thematic entity' theme and append to theme list
    theme_od = OrderedDict()
    theme_od['name'] = 'literary thematic entity'
    theme_od['aliases'] = []
    theme_od['description'] = 'A literary thematic entity, or literary theme for short, is a topic that is\nexplored in a work of fiction or an opinion that is conveyed about a topic\nin a work of fiction.'
    theme_od['notes'] = []
    theme_od['parents'] = []
    theme_od['references'] = []
    theme_od['examples'] = []
    theme_od['relatedthemes'] = []
    theme_od['source'] = ''
    themes_list.append(theme_od)

    #' return updated theme list
    return themes_list

def populate_stories_with_themes(stories_list, storythemeobjs_list):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Theme.
    Args:
        stories_list: list
        storythemeobjs_list: list
    Returns: list
    """
    story_ids = [story_od['story-id'] for i, story_od in enumerate(stories_list)]

    for storythemeobj in storythemeobjs_list:
        if not storythemeobj.name1.startswith('Collection:') and storythemeobj.name1 in story_ids:
            thematic_annotation_od = init_thematic_annotation_od(storythemeobj)
            stories_list[story_ids.index(storythemeobj.name1)]['themes'].append(thematic_annotation_od)

    return stories_list

def populate_stories_with_collection_info(storyobjs_list, stories_list):
    """
    Add collection info to stories for any collections defined in the ./notes/collections/ folder
    files.
    Args:
        storyobjs_list: list
        stories_list: list
    Returns: list
    """
    story_ids = [story_od['story-id'] for i, story_od in enumerate(stories_list)]

    for storyobj in storyobjs_list:
        if storyobj.name.startswith('Collection:'):
            component_story_names = filter(None, storyobj.components.split('\n'))
            for component_story_name in component_story_names:
                if component_story_name in story_ids:
                    stories_list[story_ids.index(component_story_name)]['collections'].append(storyobj.name)

    return stories_list

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

def write_lto_data_to_json_file(lto_json, version, output_dir, category, overwrite=False):
    """
    Write LTO information to JSON file. Set 'overwrite' to 'True' to regenerate a non-developmental
    version file.
    Args:
        lto_json: unicode
        version: string
        overwrite: boolean
    """

    #' ensure JSOn object is encoded as UTF-8
    #' failing to do so may result in an error in the case when an Ordered Dictionary of themes,
    #' stories, or collections is empty
    if isinstance(lto_json, str):
        lto_json = str(lto_json, 'UTF-8')

    #' write JSON object to file
    path = output_dir + '/' + 'lto-' + version + '-' + category + '.json'
    if not os.path.exists(path) or overwrite:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(lto_json)

def main(test_run=False):
    #' preliminaries
    basepath = GIT_THEMING_PATH_HIST
    output_dir = os.path.join(PUBLIC_DIR, 'data')
    lib.files.mkdirs(output_dir)
    os.chdir(basepath)

    #' setup git repository
    subprocess.check_output("git reset --hard origin/master".split(), stderr=subprocess.STDOUT)
    #' The first two versions (i.e. v0.1.0 and v0.1.1) are skipped on account that neither contains
    #' any themes. The tags exist for historical reasons that are unimportant here.
    versions = subprocess.check_output("git tag".split()).decode("utf-8").rstrip().split("\n")[2:]
    versions.append('dev')

    #' use version v0.3.2 for testing purposes
    if test_run:
        versions = ["v0.3.2"]

    #' create a JSON file for each named version of LTO catalogued in the repository
    for version in versions:
        lib.log.info("Caching LTO %s data...", version)

        #' retrieve theme, story, collection, and metadata for a given LTO version
        themeobjs_list, storyobjs_list, storythemeobjs_list, timestamp, commit_id = get_lto_data(version, basepath)

        #' prepare theme data and write to JSON file
        themes_list = init_themes_list(themeobjs_list, basepath)
        themes_od = OrderedDict()
        themes_od['lto'] = init_metadata_od(version, timestamp, commit_id, category='theme', count=len(themes_list))
        themes_od['themes'] = themes_list
        themes_json = json.dumps(themes_od, ensure_ascii=False, indent=4)

        #' prepare story data and write to JSON file
        stories_list = init_stories_list(storyobjs_list, basepath)
        stories_list = populate_stories_with_collection_info(storyobjs_list, stories_list)
        stories_list = populate_stories_with_themes(stories_list, storythemeobjs_list)
        stories_od = OrderedDict()
        stories_od['lto'] = init_metadata_od(version, timestamp, commit_id, category='story', count=len(stories_list))
        stories_od['stories'] = stories_list
        stories_json = json.dumps(stories_od, ensure_ascii=False, indent=4)

        #' prepare collection data and write to JSON file
        collections_list = init_collections_list(storyobjs_list, basepath)
        collections_list = populate_collections_with_component_stories_1(collections_list, storyobjs_list)
        collections_list = populate_collections_with_component_stories_2(collections_list, storyobjs_list)
        collections_list = populate_collections_with_themes(collections_list, storythemeobjs_list)
        collection_od = OrderedDict()
        collection_od['lto'] = init_metadata_od(version, timestamp, commit_id, category='collection', count=len(collections_list))
        collection_od['collections'] = collections_list
        collections_json = json.dumps(collection_od, ensure_ascii=False, indent=4)

        # ' write theme, story, and collection JSON objects to file
        # ' set overwrite to True to force existing files to be overwritten
        # ' only the developmental version should be written to file by default
        if not test_run:
            if version == 'dev':
                write_lto_data_to_json_file(themes_json, version, output_dir, category='themes', overwrite=True)
                write_lto_data_to_json_file(stories_json, version, output_dir, category='stories', overwrite=True)
                write_lto_data_to_json_file(collections_json, version, output_dir, category = 'collections', overwrite=True)
            else:
                write_lto_data_to_json_file(themes_json, version, output_dir, category='themes', overwrite=False)
                write_lto_data_to_json_file(stories_json, version, output_dir, category='stories', overwrite=False)
                write_lto_data_to_json_file(collections_json, version, output_dir, category = 'collections', overwrite=False)
