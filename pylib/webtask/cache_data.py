from __future__ import print_function
import os
from credentials import GIT_THEMING_PATH_HIST
import lib.commits
import lib.files
import lib.dataparse
import webobject
from git import Repo
import json
from collections import OrderedDict
import datetime
from pytz import timezone
import dateutil.parser

def main():
    #' preliminaries
    basepath = GIT_THEMING_PATH_HIST
    os.chdir(basepath)

    #' checkout v0.3.2 of the repo
    repo = Repo(GIT_THEMING_PATH_HIST)
    version_tags = repo.tags
    # [print(tag) for tag in repo.tags]
    version_tag = version_tags[-1]
    repo.git.checkout(version_tag)
    commit_id = repo.head.object.hexsha
    timestamp = repo.head.object.committed_datetime

    #' initialize dict object for v0.3.2 of lto
    lto_od = OrderedDict()
    metadata_od = OrderedDict()
    metadata_od['version'] = str(version_tag)
    metadata_od['timestamp'] = str(timestamp)
    metadata_od['git-commit-id'] = str(commit_id)
    lto_od['lto'] = metadata_od
    lto_od['themes'] = OrderedDict()
    print(json.dumps(lto_od, indent=4))
    #themes_list = []
    #test_theme_dict = { 'name': 'AI assistant', 'description': 'There is an artificial intelligence that acts as a personal assistant to a real person.' }
    #print(themes_list)
    #themes_list.append(test_theme_dict)
    #print(themes_list)
    #themes_list.append(test_theme_dict)
    #print(themes_list)

    # ' read theme files
    #themeobjs = []
    #for path in lib.files.walk(basepath, ".*\.th\.txt$"):
    #    if path.endswith(".th.txt"):
    #        themeobjs.extend(lib.dataparse.read_themes_from_txt(path, addextras=True, combinedescription=False))

    theme_files = list(lib.files.walk(basepath, ".*\.th\.txt$"))
    print("\n".join(theme_files))
    themeobjs = list(lib.dataparse.read_themes_from_txt(theme_files[0], addextras=True, combinedescription=False))
    fields = sorted(set(themeobjs[10].fields + themeobjs[10].extra_fields))
    #print(fields)
    json_str = webobject.Theme.make_json(themeobjs, fields=fields)
    themes = json.loads(json_str)['data']
    #print(themes[10][1])
    #print("THEME NO. 11: \n%s" % json.dumps(themes[10], indent=4))
    #print(type(fields[0]))
    #theme_dict = { 'name': {}, 'description': {}, 'parents': {} }

    id = 25
    #id = 388 # two examples
    #id = 379 # two space separated references
    fields = sorted(set(themeobjs[id].fields + themeobjs[id].extra_fields))
    print(fields)
    theme_od = OrderedDict()
    theme_od['name'] = {}
    theme_od['description'] = {}
    theme_od['parents'] = {}
    #print(theme_od)

    print(themeobjs[id].name)
    print(themeobjs[id].meta)


    for field in fields:
        if field == 'name':
            theme_od['name'] = themeobjs[id].name
        if field == 'description':
            theme_od['description'] = themeobjs[id].description.rstrip().replace(' \n','').replace('\n ','').replace('\n','')
        if field == 'parents':
            parents = themeobjs[id].parents.split(', ')
            if len(parents) == 1:
                theme_od['parents'] = ''.join(parents)
            elif len(parents) > 1:
                theme_od['parents'] = parents
        if field == 'notes':
            theme_od['notes'] = themeobjs[id].notes.rstrip().replace(' \n','').replace('\n ','').replace('\n','')
        if field == 'aliases':
            aliases = themeobjs[id].aliases
            if aliases[0] != "":
                if len(aliases) == 1:
                    theme_od['aliases'] = ''.join(aliases)
                elif len(aliases) > 1:
                    theme_od['aliases'] = aliases
        if field == 'references':
            references = filter(None, themeobjs[id].references)
            if len(references) == 1:
                if ' ' in references[0]:
                    theme_od['references'] = references[0].split(' ')
                else:
                    theme_od['references'] = ''.join(references)
            elif len(references) > 1:
                theme_od['references'] = references
        if field == 'examples':
            raw_examples = themeobjs[id].examples[0].split('\n\n')
            examples = list()
            if raw_examples[0] != "":
                for example in raw_examples:
                    examples.append(example.rstrip().replace(' \n','').replace('\n ','').replace('\n',''))
            if len(examples) == 1:
                theme_od['examples'] = ''.join(examples)
            elif len(examples) > 1:
                theme_od['examples'] = examples
        if field == 'relatedthemes':
            relatedthemes = themeobjs[id].relatedthemes
            if relatedthemes[0] != "":
                if len(relatedthemes) == 1:
                    theme_od['relatedthemes'] = ''.join(relatedthemes)
                elif len(relatedthemes) > 1:
                    theme_od['relatedthemes'] = relatedthemes
        if field == 'meta':
            theme_od['source'] = themeobjs[id].meta

    print(json.dumps(theme_od, indent=4))



main()