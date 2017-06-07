import urllib
import json
import operator as op
from collections import deque
from collections import defaultdict

from scipy.stats import hypergeom
import numpy as np

from lib.func import memoize
from lib.svgtools import SVG
import svg
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
    leaf_data, meta_data, parent_lu, ret_child_lu, toplevel = get_data()
    child_lu = defaultdict(list)
    thlevel = { th: 0 for th in roots }
    throot = { th: th for th in roots }
    remain = deque(roots)

    for theme, parents in parent_lu.iteritems():
        for parent in parents:
            child_lu[parent].append(theme)

    while remain:
        parent = remain.popleft()
        plevel = thlevel[parent]

        for child in child_lu[parent]:
            clevel = thlevel.get(child, 9999)
            if clevel > plevel + 1:
                remain.append(child)
                thlevel[child] = plevel + 1
                throot[child] = throot[parent]

    for theme, ll in thlevel.iteritems():
        if ll > level:
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




def do_make_metatheme_cube( 
    level = 2, 
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("rgb(166,85,84)", "rgb(107,140,84)", "rgb(11,112,156)", "rgb(156,122,26)"),
):
    '''
    Write an SVG image triangle of metathemes selected and color by arguments,
    positioned by relative affinities towards tos/tas/tng.
    '''
    themes_lu = themes_to_level(roots, level)
    themes = set(themes_lu)
    scores, totals = calculate_series_affinity_v1(themes)
    color_lu = { t : c for t, c in zip(roots, colors) }
    maxtot = float(max(totals.itervalues()))

    svg = SVG(style = {
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
    })
    tos, tas, tng = 'tos tas tng'.split()
    
    # make drawing
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
        color = color_lu[themes_lu[kw][1]]

        tstyle = { 
            "fill": color, 
            "font-size": "%spx" % sz,
        }
        cstyle = { 
            "fill": color, 
            "stroke": color, 
            "fill-opacity": 0.5, 
            "stroke-opacity": 0.8,
        }

        svg.text(xx, yy + sz / 2.5, kw, style = tstyle)
        svg.circle(xx, yy, radius, style = cstyle)

    np2o = sym_rot_project(1 * scale, 0 * scale, 0 * scale)
    np2a = sym_rot_project(0 * scale, 1 * scale, 0 * scale)
    np2n = sym_rot_project(0 * scale, 0 * scale, 1 * scale)
    np2o_ = -np2op
    np2a_ = -np2ap
    np2n_ = -np2np

    p2tos = np2o + origo
    p2tas = np2a + origo
    p2tng = np2n + origo
    p2tos_ = np2o_ + origo
    p2tas_ = np2a_ + origo
    p2tng_ = np2n_ + origo
    p2oo = origo

    svg.polygon((p2tos, p2tng_, p2tas, p2tos_, p2tng, p2tas_))
    
    
    # write to file
    filename = "D:\\Temp\\test.svg"
    log.info( 'Writing: %s' % filename ) 
    svg.write(filename, 1600, 1600)


if __name__ == '__main__':
    do_make_metatheme_cube()




