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
import lib.log

def init_metadata_od(version, timestamp, commit_id, theme_count):
    """
    Store LTO meta data in an ordered dictionary.
    Args:
        version: string
        timestamp: string
        commit_id: string
        theme_count: integer
    Returns: OrderedDict
    """
    metadata_od = OrderedDict()
    metadata_od['version'] = version
    metadata_od['timestamp'] = timestamp
    metadata_od['git-commit-id'] = commit_id
    metadata_od['theme-count'] = theme_count
    return metadata_od

def get_theme_objs(version, repo, basepath):
    """
    Store themes for a given version of LTO in a big list.
    Args:
        version: string
        repo: git.repo.base.Repo
        basepath: string
    Returns: list, string, string
    """
    if version == 'dev':
        repo.git.pull('origin', 'master')
    else:
        repo.git.checkout(version)
    timestamp = repo.head.object.committed_datetime.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S (UTC)')
    commit_id = str(repo.head.object.hexsha)
    themeobjs_list = list()

    #' suppress warnings for themes with missing parents fields in some older LTO versions
    broken = True if version == 'v0.2.0' or version == 'v0.3.0' else False

    for path in lib.files.walk(os.path.join(basepath, 'notes'), '.*\.th\.txt$'):
        if broken:
            themeobjs_list.extend(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False, strict=False))
        else:
            themeobjs_list.extend(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))

    return themeobjs_list, timestamp, commit_id

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
    if hasattr(themeobj, 'parents'):
        theme_od['parents'] = filter(None, [parent.strip() for parent in themeobj.parents.split(',')])
    if theme_od['parents'] == []:
        theme_od['parents'] = ['literary thematic entity']
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

def init_themes_list(themeobjs_list, basepath):
    """
    Create a list of themes, where each theme is represented by an ordered dictionary, for a given
    version of the repository. The list of themes is returned along with the timestamp and commit
    hash of the given version.
    Args:
        version: string
        repo: git.repo.base.Repo
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

def write_lto_data_to_json_file(lto_json, version, output_dir, overwrite=False):
    """
    Write LTO information to JSON file. Set 'overwrite' to 'True' to regenerate a non-developmental
    version file.
    Args:
        lto_json: unicode
        version: string
        overwrite: boolean
    """
    path = output_dir + '/' + 'lto-' + version + '-themes.json'
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
        #' create list of themes for given version of LTO
        lib.log.info("Processing LTO %s themes...", version)
        themeobjs_list, timestamp, commit_id = get_theme_objs(version, repo, basepath)
        themes_list = init_themes_list(themeobjs_list, basepath)

        # ' prepare LTO metadata to be written to JSON file
        metadata_od = init_metadata_od(version, timestamp, commit_id, theme_count=len(themes_list))

        # ' store LTO themes and metadata in an ordered dictionary
        lto_od = OrderedDict()
        lto_od['lto'] = metadata_od
        lto_od['themes'] = themes_list

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

