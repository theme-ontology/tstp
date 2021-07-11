# Copyright 2021, themeontology.org
# Tests:
import themeontology
import glob
import sys
import pandas as pd
import lib.dataparse
import lib.xls
import lib.graph


def get_ontology():
    paths = set()
    for arg in sys.argv[2:-1]:
        for item in glob.glob(arg):
            paths.add(item)
    return themeontology.read(sorted(paths))


def main():
    graph = lib.graph.KWGraph()
    filename = sys.argv[-1]
    to = get_ontology()
    data = []
    for theme in to.themes():
        for parent in theme.get("Parents").iter_parts():
            graph.makeEdge(parent.strip(), theme.name)
    topsort = graph.top_sort()
    for theme in to.themes():
        data.append([
            theme.name,
            theme.get("Parents").text_canonical_contents(),
            theme.get("Description").text_canonical_contents(),
            topsort.get(theme.name, -1),
        ])
    colnames = ["theme", "parents", "description", "level"]
    dfthemes = pd.DataFrame(columns=colnames[:4], data=data)
    print(dfthemes)
    #import pdb; pdb.set_trace()
    lib.xls.write_themelist(dfthemes, filename, columns=colnames)


