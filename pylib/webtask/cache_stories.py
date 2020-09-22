"""
Write LTO annotated thematically stories and metadata to a JSON file; one for each tagged version
in the git repository. An additional JSON file containing the LTO contents for the latest commit
is also generated.

    pyrun webtask.cache_stories (from inside the scripts directory)

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

def init_metadata_od(version, timestamp, commit_id, story_count):
    """
    Store LTO meta data in an ordered dictionary.
    Args:
        version: string
        timestamp: string
        commit_id: string
        story_count: integer
    Returns: OrderedDict
    """
    metadata_od = OrderedDict()
    metadata_od['version'] = version
    metadata_od['timestamp'] = timestamp
    metadata_od['git-commit-id'] = commit_id
    metadata_od['story-count'] = story_count
    return metadata_od

def get_story_objs(version, repo, basepath):
    """
    Store story metadata and thematic annotations for a given version of LTO in a big lists.
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
    #' do not create list entries for collections
    if storyobj.name.startswith('Collection:'):
        story_od = None
    else:
        fields = [
            'storyid',
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
        story_od['storyid'] = storyobj.name
        story_od['title'] = storyobj.title
        story_od['date'] = storyobj.date
        #' the split on three newlines is needed to get rid of the story references which are
        #' included at the end of the description
        story_od['description'] = storyobj.description.rstrip().split('\n\n\n')[0]
        story_od['collections'] = filter(None, storyobj.collections.split('\n'))
        story_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(storyobj.meta)['source'])
        if hasattr(storyobj, 'genre'):
            story_od['genres'] = filter(None, [genre.strip() for genre in storyobj.genre.split(',')])
        if hasattr(storyobj, 'references'):
            story_od['references'] = filter(None, storyobj.references.split('\n'))

    return story_od

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

def populate_stories_with_themes(stories_list, storythemeobjs_list):
    """
    Initialize an ordered dictionary and populate its entries with the preprocessed fields of a
    TSTPObject object of category Theme.
    Args:
        stories_list: list
        storythemeobjs_list: list
    Returns: list
    """
    story_ids = [story_od['storyid'] for i, story_od in enumerate(stories_list)]

    for storythemeobj in storythemeobjs_list:
        if storythemeobj.name1.startswith('Collection:') == False and storythemeobj.name1 in story_ids:
            thematic_annotation_od = init_thematic_annotation_od(storythemeobj)
            stories_list[story_ids.index(storythemeobj.name1)]['themes'].append(thematic_annotation_od)

    return stories_list

def filter_empty_stories(stories_list):
    """
    Excise any stories without themes from the list of stories.
    Args:
        stories_list: list
    Returns: list
    """
    empty_stories = []
    for story in stories_list:
        if story['themes'] == []:
            empty_stories.append(story['storyid'])
    result = []
    for story in stories_list:
        if story['storyid'] not in empty_stories:
            result.append(story)

    return result

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
        if storyobj.name.startswith('Collection:') == False:
            story_od = init_story_od(storyobj, basepath)
            stories_list.append(story_od)

    # ' sort stories by increasing order of release data
    stories_list = sorted(stories_list, key=lambda i: i['date'])

    return stories_list

def write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=False):
    """
    Write LTO information to JSON file. Set 'overwrite' to 'True' to regenerate a non-developmental
    version file.
    Args:
        lto_json: unicode
        version: string
        overwrite: boolean
    """
    path = output_dir + '/' + 'lto-' + version + '-stories.json'
    if not os.path.exists(path) or overwrite:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(lto_json)

def main():
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

    #' create a JSON file for each named version of LTO catalogued in the repository
    for version in versions:
        #' create list of themes for given version of LTO
        lib.log.info("Processing LTO %s stories...", version)
        storyobjs_list, storythemeobjs_list, timestamp, commit_id = get_story_objs(version, repo, basepath)

        #' convert story objects to list of story ordered dictionaries
        stories_list = init_stories_list(storyobjs_list, basepath)
        stories_list = populate_stories_with_themes(stories_list, storythemeobjs_list)

        #' filter empty stories
        story_list = filter_empty_stories(stories_list)

        # ' prepare LTO metadata to be written to JSON file
        metadata_od = init_metadata_od(version, timestamp, commit_id, story_count=len(stories_list))

        # ' store LTO themes and metadata in an ordered dictionary
        lto_od = OrderedDict()
        lto_od['lto'] = metadata_od
        lto_od['stories'] = stories_list

        # ' convert LTO ordered dictionary to JSON format
        lto_json = json.dumps(lto_od, ensure_ascii=False, indent=4)

        #' write LTO JSON object to file
        #' set overwrite to True to force existing files to be overwritten
        #' only the developmental version should be written to file by default
        if version == 'dev':
            write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=True)
        else:
            write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=False)

