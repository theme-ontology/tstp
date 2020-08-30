"""
Write LTO themes and metadata to a JSON file; one for each tagged version in the git repository. An
additional JSON file containing the LTO contents for the latest commit is also generated.

    pyrun webtask.cache_themes (from inside the scripts directory)

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

def init_metadata_od(version, timestamp, commit_id, theme_count):
    """
    Store LTO meta data in an ordered dictionary.
    Args:
        version: string
        timestamp: string
        git_commit_id: string
        theme_count: integer
    Returns: OrderedDict
    """
    metadata_od = OrderedDict()
    metadata_od['version'] = version
    metadata_od['timestamp'] = timestamp
    metadata_od['git-commit-id'] = commit_id
    metadata_od['theme-count'] = theme_count
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
    theme_od['description'] = themeobj.description.rstrip()
    theme_od['parents'] = filter(None, [parent.strip() for parent in themeobj.parents.split(',')])
    theme_od['source'] = '.' + lib.files.abspath2relpath(basepath, json.loads(themeobj.meta)['source'])
    extra_fields = set(themeobj.extra_fields)
    if 'aliases' in extra_fields:
        theme_od['aliases'] = filter(None, [alias.strip() for alias in themeobj.aliases.split(',')])
    if 'notes' in extra_fields:
        theme_od['notes'] = themeobj.notes.rstrip()
    if 'references' in extra_fields:
        theme_od['references'] = filter(None, themeobj.references.split('\n'))
    if 'examples' in extra_fields:
        theme_od['examples'] = filter(None, themeobj.examples.split('\n'))
    if 'relatedthemes' in extra_fields:
        theme_od['relatedthemes'] = filter(None, [relatedtheme.strip() for relatedtheme in themeobj.relatedthemes.split(',')])
    return theme_od

def sort_themes(themes_list):
    """
    Sort a list of theme ordered dictionary objects in alphabetical order of the 'name' field.
    Args:
        theme_list: list
    Returns: list
    """
    return sorted(themes_list, key=lambda i: i['name'][0].lower())

def write_lto_data_to_json_file(lto_od, version, output_dir, overwrite=False):
    """
    Write LTO information to JSON file. Set 'overwrite' to 'True' to regenerate a non-developmental
    version file.
    Args:
        lto_od: OrderedDict
        version: string
        overwrite: boolean
    """
    path = output_dir + '/' + 'lto-' + version + '.json'
    if not os.path.exists(path) or overwrite:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(lto_od, ensure_ascii=False, indent=4))

def lto_to_json(repo, version_tag, basepath, output_dir, overwrite=False):
    """
    Preprocess LTO themes and metadata and output to JSON file.
    Args:
        repo: git.repo.base.Repo
        version_tag: git.refs.tag.TagReference
        basepath: string
        output_dir: string
        overwrite: boolean
    """
    version = str(version_tag)
    print(version)
    path = output_dir + '/' + 'lto-' + version + '.json'
    if not os.path.exists(path) or overwrite:
        repo.git.checkout(version_tag)
        commit_id = str(repo.head.object.hexsha)
        timestamp = repo.head.object.committed_datetime.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S (UTC)")

        # ' read theme files
        themes_list = list()
        for path in lib.files.walk(basepath, ".*\.th\.txt$"):
            themeobjs = list(
                lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))
            for themeobj in themeobjs:
                theme_od = init_theme_od(themeobj, basepath)
                themes_list.append(theme_od)

        # ' sort themes in alphabetical order
        themes_list_sorted = sort_themes(themes_list)

        # ' prepare LTO metadata to be written to JSON file
        metadata_od = init_metadata_od(version, timestamp, commit_id, theme_count=len(themes_list))

        # ' store LTO themes and metadata in an ordered dictionary
        lto_od = OrderedDict()
        lto_od['lto'] = metadata_od
        lto_od['themes'] = themes_list_sorted

        # ' write to JSON file
        write_lto_data_to_json_file(lto_od, version, output_dir)


def main():
    #' preliminaries
    basepath = GIT_THEMING_PATH_HIST
    output_dir = os.path.join(PUBLIC_DIR, 'data')
    lib.files.mkdirs(output_dir)
    os.chdir(basepath)

    #' setup git repository
    repo = Repo(GIT_THEMING_PATH_HIST)
    #' The first two versions (i.e. v0.1.0 and v0.1.1) are skipped on account that neither contains
    #' any themes. They exist as tags for historical reasons that are uminportant here.
    version_tags = repo.tags[2:]

    #' create a JSON file for each named version of LTO catalogued in the repository
    for version_tag in version_tags:
        lto_to_json(repo, version_tag, basepath, output_dir, overwrite=False)

    # ' create a JSON file for the latest version of LTO in the repository
    version = 'developmental'
    version_short = 'dev'
    print(version_short)
    repo.git.pull('origin','master')
    commit_id = repo.head.object.hexsha
    timestamp = repo.head.object.committed_datetime.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S (UTC)")

    # ' prepare LTO themes to be written to JSON file
    themes_list = list()
    for path in lib.files.walk(basepath, ".*\.th\.txt$"):
        themeobjs = list(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))
        for themeobj in themeobjs:
            theme_od = init_theme_od(themeobj, basepath)
            themes_list.append(theme_od)

    #' sort themes in alphabetical order
    themes_list_sorted = sort_themes(themes_list)

    #' prepare LTO metadata to be written to JSON file
    metadata_od = init_metadata_od(version, timestamp, commit_id, theme_count = len(themes_list))

    #' store LTO themes and metadata in an ordered dictionary
    lto_od = OrderedDict()
    lto_od['lto'] = metadata_od
    lto_od['themes'] = themes_list_sorted

    #' write to JSON file
    write_lto_data_to_json_file(lto_od, version_short, output_dir, overwrite=True)


