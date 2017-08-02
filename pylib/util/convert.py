import sys
import log
import os

import webdb
import webobject
import lib.xls

def read_themes(filename):
    headers = [
        "Keyword", 
        "Implications", 
        "Definition", 
    ]
    themes, sheetcount, rowcount = lib.xls.read_xls(filename, headers)
        
    for keyword, parents, description in sorted(themes):
        yield webobject.Theme.create(
            name = keyword,
            description = description,
            parents = parents,
        )        


def main():
    method = sys.argv[-2]
    target = os.path.abspath(sys.argv[-1])

    if method == "themedefs":
        objs = list(read_themes(target))
        txt = webdb.get_defenitions_text_for_objects(objs)
        print txt.encode("utf-8")
