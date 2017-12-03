import lib.datastats
import lib.log
from lib.mathnp import savitzky_golay
from collections import defaultdict, deque
import numpy as np
import lib.svg


lib.log.redirect()


def main():
    make_viz()


def smooth(a):
    return np.maximum(0, savitzky_golay(a, 7, 3)) ** 0.5


def make_pts(aa, yy, dx, width, dy = 13.0, ddy = 30.0):
    pts = []

    for i, y in enumerate(aa):
        p = (i * dx, yy + ddy - y * dy)
        if pts:
            py = pts[-1][1]
            pts.append((p[0], py))
        pts.append(p)

    pts.append((width, pts[-1][1]))
    pts.append((width, yy + ddy))
    pts.append((0, yy + ddy))

    return pts


def make_viz():
    roots = [
        "the human condition",
        "society",
        "the pursuit of knowledge",
        "alternate reality",
    ]
    colors = {
        "the human condition": "#6F0F0F",
        "society": "#176F0F",
        "the pursuit of knowledge": "#0F0F6F",
        "alternate reality": "#6F5F0F",
    }
    prefixes = {
        'tos': 0,
        'tas': 1,
        'tng': 2,
    }
    weights = {
        'minor': 0,
        'major': 1,
        'choice': 2,
    }
    svg = lib.svg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "14px",
            "font-weight": "bold",
            "fill": "#333333",
            "text-anchor": "start",
        },
        "polygon.themeweight2": {
            "fill": "#000000",
        },
        "polygon.themeweight1": {
            "fill": "#666666",
            "fill-opacity": "0.75",
            "filter": "brightness(180%) saturate(50%)",
        },
        "polygon.themeweight0": {
            "fill": "#dddddd",
        },
        "line.treeline": {
            "stroke": "#000000",
            "stroke-dasharray": "2, 1",
        },
        "line.gridmajor": {
            "stroke": "#666666",
            "stroke-dasharray": "1, 1",
        },
        "line.gridminor": {
            "stroke": "#666666",
            "stroke-dasharray": "1, 2",
        },
        "circle.treenode": {
            "fill": "#000000",
        },
    })

    parents_lu, children_lu, lforder = lib.datastats.get_theme_tree()
    themes_lu = lib.datastats.metathemes_with_usage()
    leafthemes_lu = lib.datastats.themes_with_usage()
    levels = lib.datastats.get_metathemes_by_level()
    metathemes = {}
    leafthemes = []
    sids = set()

    for theme, obj in leafthemes_lu.iteritems():
        score = 0

        for sid, st in obj.stories.iteritems():
            if sid[:3] in prefixes:
                score += weights[st.weight] * 3 + 1

        leafthemes.append((score, theme, obj.stories, obj.parents.split(",")[0]))

    leafthemes.sort(reverse = True)

    for level, themes in enumerate(levels):
        for theme in themes:
            metathemes[theme] = level
            for sid in themes_lu[theme]:
                pp = sid[:3]
                if pp in prefixes:
                    sids.add(("%s%s" % (prefixes[pp], sid[3:]), sid))

    sids = { s[1]: i for i, s in enumerate(sorted(sids)) }
    dfs = list((0, t) for t in reversed(roots))
    visited = set()

    width = 1000.0
    yy = 0
    dx = width / len(sids)
    color = "#000000"
    plevel = -1
    levelyy = {}
    groupspacing = 30
    textoffset = 15

    for pf in prefixes:
        for ss in xrange(1, 8):
            sid = "%s%sx01" % (pf, ss)
            if sid in sids:
                xx = sids[sid] * dx
                svg.line(xx, 0, xx, 7000, cls = "gridminor" if ss > 1 else "gridmajor")

    def drawit(aa, xx, yy, theme, level, plevel, color, compact = False, ccolor = "#000000"):
        ddy = 10 if compact else 30
        dy = 6 if compact else 13

        svg.line(0, yy + ddy, width, yy + ddy, cls = "gridminor")
        pts = make_pts(aa[0] + aa[1] + aa[2], yy, dx, width, dy, ddy)
        svg.polygon(pts, cls = "themeweight0")
        pts = make_pts(aa[1] + aa[2], yy, dx, width, dy, ddy)
        svg.polygon(pts, cls = "themeweight1", style = { "fill": color })
        pts = make_pts(aa[2], yy, dx, width, dy, ddy)
        svg.polygon(pts, cls = "themeweight2")

        if not compact:
            svg.text(25 + 15 * level, yy + textoffset, theme)

        elevel = max(0, min(level, plevel))
        x1 = 10 + 15 * elevel
        x2 = 22 + 15 * level
        xx2 = max(x1, 10 + 15 * level)
        y2 = yy + textoffset - 3

        if level > 0:
            y1 = levelyy[elevel] + textoffset - 3
            svg.line(x1, y1, x1, y2, cls = "treeline")
            svg.line(x1, y2, x2, y2, cls = "treeline")
            svg.line(x1, y1, x1, y2, cls = "treeline")

        if compact:
            y2 -= 7

        radius = 3 if ccolor == "#000000" else 4 if compact else 5

        svg.circle(xx2, y2, radius, cls = "treenode", style = { "fill": ccolor })

    while dfs:
        level, theme = dfs.pop()
        nlevel = [ ch for ch in sorted(children_lu[theme]) if ch in metathemes and ch not in visited ]
        dfs.extend((metathemes[t], t) for t in reversed(nlevel))
        visited.update(nlevel)

        stories = themes_lu[theme]
        aa = [ np.zeros(len(sids)) for _ in xrange(3) ]

        if theme in roots:
            yy += groupspacing
            color = colors[theme]

        for sid, st in stories.iteritems():
            ii = sids.get(sid, None)
            jj = weights[st.weight]

            if ii is not None:
                aa[jj][ii] = 1

        for i, a in enumerate(aa):
            aa[i] = np.maximum(a, smooth(a))

        drawit(aa, xx, yy, theme, level, plevel, color)

        plevel = level
        levelyy[level] = yy
        yy += groupspacing

    yy += groupspacing

    for idx, (score, theme, stories, parent) in enumerate(leafthemes[:70]):
        while parents_lu[parent]:
            parent = parents_lu[parent][0]

        aa = [ np.zeros(len(sids)) for _ in xrange(3) ]

        for sid, st in stories.iteritems():
            ii = sids.get(sid, None)
            jj = weights[st.weight]

            if ii is not None:
                aa[jj][ii] = 1

        for i, a in enumerate(aa):
            aa[i] = np.maximum(a, smooth(a))

        drawit(aa, xx, yy, theme, 0, -1, "#444444", idx > 30, colors[parent])

        if idx == 30:
            yy += 10

        yy += groupspacing if idx <= 30 else 10

    print svg.make(1000, 8000)

