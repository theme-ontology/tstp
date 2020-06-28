from __future__ import print_function
import lib.datastats
import lib.log
import lib.mosvg
import sys
import tempfile
import os.path
import lib.files


lib.log.redirect()
DOT_CMD = "dot"


def main():
    path = sys.argv[-1] if len(sys.argv) > 2 else "."
    write_to_path(path)


def write_to_path(path):
    graph = lib.datastats.get_theme_graph()
    roots = graph.findRoots()
    l2, l3 = [], []
    lib.files.remove(path)

    for root in roots:
        for child in graph.findNeighbours(root):
            l2.append(child)
    for root in l2:
        for child in graph.findNeighbours(root):
            nodecount = len(graph.restrict(roots=[child]).nodes)
            levels = len(set(graph.top_sort(roots=[child]).values()))
            if levels > 2 and nodecount > 4:
                l3.append(child)
    for pref, tlist in [("", roots), ("Level-2", l2), ("Level-3", l3)]:
        lib.files.mkdirs(os.path.join(path, pref))
        for root in tlist:
            tmppath = tempfile.gettempdir()
            fname = root.replace(" ", "_").encode("ascii", "ignore")
            dotfile = graph.make_dot_graph(tmppath, fname, roots=[root])
            pdffile = os.path.join(path, pref, fname + '.pdf')
            CMD_DOT = r'""%s"" -Tpdf -o%%s %%s' % DOT_CMD
            os.system(CMD_DOT % (pdffile, dotfile))
            lib.log.info(CMD_DOT % (pdffile, dotfile))


def iter_colors():
    colors = [
        "#393b79", "#5254a3", "#6b6ecf", "#9c9ede",
        "#637939", "#8ca252", "#b5cf6b", "#cedb9c",
        "#8c6d31", "#bd9e39", "#e7ba52", "#e7cb94",
        "#843c39", "#ad494a", "#d6616b", "#e7969c",
        "#7b4173", "#a55194", "#ce6dbd", "#de9ed6",
    ]
    while True:
        for c in colors:
            yield c

