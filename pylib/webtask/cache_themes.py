from __future__ import print_function
import os
from credentials import GIT_THEMING_PATH_HIST
from credentials import PUBLIC_DIR
import lib.commits
import lib.files
import lib.dataparse
import webobject
from git import Repo
import json
import io
from collections import OrderedDict
import pytz

def main():
    #' preliminaries
    basepath = GIT_THEMING_PATH_HIST
    output_dir = os.path.join(PUBLIC_DIR,"data")
    print(output_dir)
    lib.files.mkdirs(output_dir)
    os.chdir(basepath)

    #' construct jsonification of lto themes for each version and write to file
    repo = Repo(GIT_THEMING_PATH_HIST)
    version_tags = repo.tags
    # [print(tag) for tag in repo.tags]

    for version_tag in version_tags:
        print(version_tag)
        repo.git.checkout(version_tag)
        commit_id = repo.head.object.hexsha
        dt = repo.head.object.committed_datetime.astimezone(pytz.UTC)
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S (UTC)")
        lto_od = OrderedDict()
        metadata_od = OrderedDict()
        metadata_od['version'] = str(version_tag)
        metadata_od['timestamp'] = str(timestamp)
        metadata_od['git-commit-id'] = str(commit_id)

        # ' read theme files
        themes_list = list()
        for path in lib.files.walk(basepath, ".*\.th\.txt$"):
            themeobjs = list(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))
            for themeobj in themeobjs:
                fields = sorted(set(themeobj.fields + themeobj.extra_fields))
                theme_od = OrderedDict()
                if 'name' in fields:
                    theme_od['name'] = themeobj.name
                if 'description' in fields:
                    theme_od['description'] = themeobj.description.rstrip()
                if 'aliases' in fields:
                    aliases = themeobj.aliases
                    if aliases[0] != "":
                        if len(aliases) == 1:
                            theme_od['aliases'] = ''.join(aliases)
                        elif len(aliases) > 1:
                            theme_od['aliases'] = aliases
                if 'notes' in fields:
                    theme_od['notes'] = themeobj.notes[0].rstrip()
                if 'parents' in fields:
                    parents = themeobj.parents.split(', ')
                    if len(parents) == 1:
                        theme_od['parents'] = ''.join(parents)
                    elif len(parents) > 1:
                        theme_od['parents'] = parents
                if 'references' in fields:
                    references = filter(None, themeobj.references)
                    if len(references) == 1:
                        if ' ' in references[0]:
                            theme_od['references'] = references[0].split(' ')
                        else:
                            theme_od['references'] = ''.join(references)
                    elif len(references) > 1:
                        theme_od['references'] = references
                if 'examples' in fields:
                    raw_examples = themeobj.examples[0].split('\n\n')
                    examples = list()
                    if raw_examples[0] != "":
                        for example in raw_examples:
                            examples.append(example.rstrip())
                    if len(examples) == 1:
                        theme_od['examples'] = ''.join(examples)
                    elif len(examples) > 1:
                        theme_od['examples'] = examples
                if 'relatedthemes' in fields:
                    relatedthemes = themeobj.relatedthemes
                    if relatedthemes[0] != "":
                        if len(relatedthemes) == 1:
                            theme_od['relatedthemes'] = ''.join(relatedthemes)
                        elif len(relatedthemes) > 1:
                            theme_od['relatedthemes'] = relatedthemes
                if 'meta' in fields:
                    meta = json.loads(themeobj.meta)
                    source_path = meta['source']
                    theme_od['source'] = '.' + lib.files.abspath2relpath(basepath, source_path)
                themes_list.append(theme_od)

        themes_list = sorted(themes_list, key=lambda i: i['name'].lower())
        print(len(themes_list))
        metadata_od['theme-count'] = len(themes_list)
        lto_od['lto'] = metadata_od
        lto_od['themes'] = themes_list

        if len(themes_list) > 0:
            output_file = 'lto-' + str(version_tag) + '.json'
            with io.open(output_dir + '/' + output_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(lto_od, ensure_ascii=False, indent=4))


    # ' construct jsonification of current lto themes and write to file
    print('dev')
    repo.git.pull('origin','master')
    commit_id = repo.head.object.hexsha
    dt = repo.head.object.committed_datetime.astimezone(pytz.UTC)
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S (UTC)")
    lto_od = OrderedDict()
    metadata_od = OrderedDict()
    metadata_od['version'] = 'developmental'
    metadata_od['timestamp'] = str(timestamp)
    metadata_od['git-commit-id'] = str(commit_id)

    # ' read theme files
    themes_list = list()
    for path in lib.files.walk(basepath, ".*\.th\.txt$"):
        themeobjs = list(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))
        for themeobj in themeobjs:
            fields = sorted(set(themeobj.fields + themeobj.extra_fields))
            theme_od = OrderedDict()
            if 'name' in fields:
                theme_od['name'] = themeobj.name
            if 'description' in fields:
                theme_od['description'] = themeobj.description.rstrip()
            if 'aliases' in fields:
                aliases = themeobj.aliases
                if aliases[0] != "":
                    if len(aliases) == 1:
                        theme_od['aliases'] = [''.join(aliases)]
                    elif len(aliases) > 1:
                        theme_od['aliases'] = aliases
            if 'notes' in fields:
                theme_od['notes'] = themeobj.notes[0].rstrip()
            if 'parents' in fields:
                parents = themeobj.parents.split(', ')
                if len(parents) == 1:
                    theme_od['parents'] = [''.join(parents)]
                elif len(parents) > 1:
                    theme_od['parents'] = parents
            if 'references' in fields:
                references = filter(None, themeobj.references)
                if len(references) == 1:
                    if ' ' in references[0]:
                        theme_od['references'] = [references[0].split(' ')]
                    else:
                        theme_od['references'] = [''.join(references)]
                elif len(references) > 1:
                    theme_od['references'] = references
            if 'examples' in fields:
                raw_examples = themeobj.examples[0].split('\n\n')
                examples = list()
                if raw_examples[0] != "":
                    for example in raw_examples:
                        examples.append(example.rstrip())
                if len(examples) == 1:
                    theme_od['examples'] = [''.join(examples)]
                elif len(examples) > 1:
                    theme_od['examples'] = examples
            if 'relatedthemes' in fields:
                relatedthemes = themeobj.relatedthemes
                if relatedthemes[0] != "":
                    if len(relatedthemes) == 1:
                        theme_od['relatedthemes'] = [''.join(relatedthemes)]
                    elif len(relatedthemes) > 1:
                        theme_od['relatedthemes'] = relatedthemes
            if 'meta' in fields:
                meta = json.loads(themeobj.meta)
                source_path = meta['source']
                theme_od['source'] = '.' + lib.files.abspath2relpath(basepath, source_path)
            themes_list.append(theme_od)

    themes_list = sorted(themes_list, key=lambda i: i['name'][0].lower())
    print(len(themes_list))

    metadata_od['theme-count'] = len(themes_list)
    lto_od['lto'] = metadata_od
    lto_od['themes'] = themes_list

    if len(themes_list) > 0:
        output_file = 'lto-dev.json'
        with io.open(output_dir + '/' + output_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(lto_od, ensure_ascii=False, indent=4))


