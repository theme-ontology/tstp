import urllib
import json
import operator as op
from collections import deque
from collections import defaultdict

from scipy.stats import hypergeom
import numpy as np

from lib.func import memoize
import lib.svg
import log
from copy import deepcopy

BASE_URL = "http://127.0.0.1/tstp/webui/json.php?"


def rotate(v, a, b):
    """
    Rotate 3d vector vv by aa and bb degres.
    """
    a = np.radians(a)
    b = np.radians(b)
    ca = np.cos(a)
    sa = np.sin(a)
    cb = np.cos(b)
    sb = np.sin(b)
    M1 = np.array([
        [+ca, -sa, 0],
        [+sa, +ca, 0],
        [  0,   0, 1],
    ])
    M2 = np.array([
        [+cb, 0, +sb],
        [  0, 1,   0],
        [-sb, 0, +cb],
    ])
    M3 = np.array([
        [  1,   0,   0],
        [  0, +ca, -sa],
        [  0, +sa, +ca],
    ])
    
    return v.dot(M3).dot(M2)


def sym_rot_project(x, y, z):
    """
    Rotate as to see cube from corner and return x, y. 
    """
    a = -45
    b = 35.2644
    v = np.array([x, y, z], dtype=float)
    r = rotate(v, a, b)
    return r[:2]


def norm(v):
    return v.dot(v) ** 0.5


def cphyper(k, K, n, N):
    return 1.0 - hypergeom.cdf(k - 1, N, n, K)

def phyper(k, K, n, N):
    return hypergeom.pmf(k, N, n, K)


@memoize
def get_data():
    url = BASE_URL + "action=metathemedata"
    response = urllib.urlopen(url)
    ret_data = json.loads(response.read())
    return ret_data


def merged_theme_data(d1, d2):
    """
    Merge two { theme1 => [(sid1, weight1), ...], ... } type
    distionaries into one.
    """
    dd_ret = {}
    keys = set(d1.keys() + d2.keys())

    for theme in keys:
        items1 = d1.get(theme, [])
        items2 = d2.get(theme, [])
        dd_ret[theme] = sorted(set(tuple(x) for x in (items1 + items2)))

    return dd_ret


def themes_to_level(roots, level):
    """
    @returns
        { theme1 => (level1, root1), ... }
    """
    leaf_data, meta_data, parent_lu, child_lu, toplevel = get_data()
    thlevel = { th: 0 for th in roots }
    throot = { th: th for th in roots }
    remain = deque(roots)

    while remain:
        parent = remain.popleft()
        plevel = thlevel[parent]

        for child in child_lu.get(parent, []):
            clevel = thlevel.get(child, 9999)
            if clevel > plevel + 1:
                remain.append(child)
                thlevel[child] = plevel + 1
                throot[child] = throot[parent]

    for theme, ll in thlevel.iteritems():
        if level == -1 and theme in child_lu:
            throot[theme] = (ll, throot[theme])
        elif ll > level:
            del throot[theme]
        else:
            throot[theme] = (ll, throot[theme])

    return throot


def calculate_series_affinity_v1(themes):
    """
    Score each used theme for tos/tas/tng repsectively using 
    a simple counting heuristic.
    """
    leaf_data, meta_data, parent_lu, ret_child_lu, toplevel = get_data()
    tos, tas, tng = 'tos tas tng'.split()
    tosc, tasc, tngc = 80, 22, 178
    nc = tosc + tasc + tngc
    scope = ("minor", "major")
    counts = defaultdict(lambda: defaultdict(float))
    data = merged_theme_data(leaf_data, meta_data)

    for theme, items in data.iteritems():
        if theme in themes:
            for sid, ww in items:
                series = sid[:3].lower()
                if ww in scope and series in (tos, tas, tng):
                    counts[theme][series] += 1.0
        
    # calculate all p-values by hypergeometric test
    totals = {}
    scores = defaultdict(lambda: defaultdict(float))

    for theme in counts.keys():
        count = sum(x for x in counts[theme].itervalues())
        totals[theme] = count
        for series, seriesc in zip((tos, tas, tng), (tosc, tasc, tngc)):
            tscount = counts[theme][series]
            pvalue = cphyper(tscount, seriesc, count, nc)
            scores[theme][series] = pvalue

    # sort and calculate ordinal score
    scores2 = defaultdict(lambda: defaultdict(float))

    for series, seriesc in zip((tos, tas, tng), (tosc, tasc, tngc)):
        thorder = []
        for theme in counts.keys():
            thorder.append((scores[theme][series], theme))
        thorder.sort(reverse = True)
        for idx, (_, theme) in enumerate(thorder):
            scores2[theme][series] = idx / float(len(thorder))
            
    return scores2, totals


def get_viz_data(
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("#6F0F0F", "#176F0F", "#0F0F6F", "#6F5F0F"),
):
    """
    Compose the dataset needed for this visualization. It may be published for D3 later.
    """

def do_make_metatheme_cube( 
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("#6F0F0F", "#176F0F", "#0F0F6F", "#6F5F0F"),
):
    '''
    Write an SVG image triangle of metathemes selected and color by arguments,
    positioned by relative affinities towards tos/tas/tng.
    '''
    themes_lu = themes_to_level(roots, -1)
    themes = set(t for t, (l, _) in themes_lu.iteritems())
    #tinythemes = set(t for t in themes_lu if t not in themes)
    scores, totals = calculate_series_affinity_v1(themes)
    color_lu = { t : c for t, c in zip(roots, colors) }
    maxtot = float(max(totals.itervalues()))

    svg = lib.svg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "8px",
            "fill": "#333333",
            "text-anchor": "middle",
        },
        "polyline": {
            "stroke": "#333333",
            "stroke-width": "4px",
            "fill-opacity": "0.1",
        },
        "polygon": {
            "stroke": "#333333",
            "stroke-width": "2px",
            "fill": "none",
        },
        ".axis": {
            "stroke": "#333333",
            "stroke-width": "2px",
        },
        ".border": {
            "stroke": "#cccccc",
            "stroke-width": "1px",
        },
        ".grid": {
            "stroke": "#444444",
            "stroke-width": "1px",
            "stroke-dasharray": "1, 2",
        },
    })
    svg.marker("arrow", svg.stock.arrowhead(6), scale = 2)
    sgrid = svg['grid']
    sdata = svg['data']

    tos, tas, tng = 'tos tas tng'.split()
    lines = []
    scale = 500.0
    origo = np.array([500, 500])
    font_min = 7.0
    circle_min = 8
    textlines = []
    dotlines = []

    for kw, data in scores.iteritems():
        x1 = data[tng] * scale
        x2 = data[tas] * scale
        x3 = data[tos] * scale
        xx, yy = sym_rot_project(x1, x2, x3) + origo
            
        sz = font_min + (totals[kw] / maxtot) ** 0.5 * 10.0 * 4 / len(roots)
        radius = circle_min + (totals[kw] / maxtot) ** 0.5 / len(roots) * 100
        level, root = themes_lu[kw]
        color = color_lu[root]

        tstyle = { 
            "fill": color, 
            "font-size": "%spx" % sz,
        }
        cstyle = { 
            "fill": color, 
            "stroke": color, 
            "fill-opacity": 0.5, 
            "stroke-opacity": 0.7,
        }

        if level < 99:
            sdata.text(xx, yy + sz / 2.5, kw, style = tstyle)
            sdata.circle(xx, yy, radius, style = cstyle)
        else:
            sdata.circle(xx, yy, 2, style = cstyle)

    np2o = sym_rot_project(1 * scale, 0 * scale, 0 * scale)
    np2a = sym_rot_project(0 * scale, 1 * scale, 0 * scale)
    np2n = sym_rot_project(0 * scale, 0 * scale, 1 * scale)
    backorigo = origo + sym_rot_project(1, 1, 1)

    p2tos = origo + np2o
    p2tas = origo + np2a
    p2tng = origo + np2n
    p2tos_ = origo - np2o
    p2tas_ = origo - np2a
    p2tng_ = origo - np2n
    ox, oy = origo
    box, boy = backorigo

    sgrid.polygon((p2tos, p2tng_, p2tas, p2tos_, p2tng, p2tas_), cls = "border")

    with sgrid.clip() as mask:
        mask.polygon((p2tos, p2tng_, p2tas, p2tos_, p2tng, p2tas_))

        for ss in xrange(1, 15):
            sscale = ss / 14.0 * 2
            pps = [ origo + pt * sscale for pt in [np2o, np2a, np2n] ]
            sgrid.polygon(pps, cls = "grid")

    for pt in [np2o, np2a, np2n]:
        xx, yy = origo - pt * 1.05
        sgrid.line(ox, oy, xx, yy, cls = "border")

    for pt in [np2o, np2a, np2n]:
        xx, yy = origo + pt * 1.02
        sgrid.line(ox, oy, xx, yy, markers = (None, "arrow"), cls = "axis")
    
    return svg


if __name__ == '__main__':
    svg = do_make_metatheme_cube()
    print svg.make(1600, 1600)

    # write to file
    #filename = "D:\\Temp\\test.svg"
    #log.info( 'Writing: %s' % filename ) 
    #svg.write(filename, 1600, 1600)




