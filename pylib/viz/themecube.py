import urllib
import json
import operator as op
from collections import deque
from collections import defaultdict
import re

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


def sid_to_set(sid, tests):
    """
    Map a list of sids to named sets.
    """
    for name, pattern in tests.iteritems():
        if pattern.match(sid):
            return name


def calculate_series_affinity_v1(themes, themesets, scope):
    """
    Score each used theme for tos/tas/tng repsectively using 
    a simple counting heuristic.
    """
    setnames = [ x[0] for x in themesets ]
    tests = { name : re.compile(pattern) for name, pattern in themesets }
    sidsets = { name: set() for name in tests }

    leaf_data, meta_data, parent_lu, ret_child_lu, toplevel = get_data()

    counts = defaultdict(lambda: defaultdict(float))
    data = merged_theme_data(leaf_data, meta_data)
    done = defaultdict(int)

    for theme, items in data.iteritems():
        if theme in themes:
            for sid, ww in items:
                setname = sid_to_set(sid, tests)

                if ww in scope and setname:
                    done[(theme, sid)] += 1
                    if done[(theme, sid)] == 1: # avoid double-counting choice/major
                        sidsets[setname].add(sid)
                        counts[theme][setname] += 1.0
        

    # calculate all p-values by hypergeometric test
    totals = {}
    scores = defaultdict(lambda: defaultdict(float))
    nc = sum(len(s) for s in sidsets.itervalues())

    for theme in counts.keys():
        count = sum(x for x in counts[theme].itervalues())
        totals[theme] = count

        for setname in setnames:
            seriesc = len(sidsets[setname])
            tscount = counts[theme][setname]
            pvalue = cphyper(tscount, seriesc, count, nc)
            scores[theme][setname] = pvalue

    # sort and calculate ordinal score
    scores2 = defaultdict(lambda: defaultdict(float))

    for setname in setnames:
        seriesc = len(sidsets[setname])
        thorder = []

        for theme in counts.keys():
            thorder.append((scores[theme][setname], theme))

        thorder.sort(reverse = True)

        for idx, (_, theme) in enumerate(thorder):
            scores2[theme][setname] = idx / float(len(thorder))
            
    return scores2, totals


def get_viz_data(
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("#6F0F0F", "#176F0F", "#0F0F6F", "#6F5F0F"),
    themesets = (
        ("tos", "tos[0-3]x\\d\\d"), 
        ("tas", "tas[1-2]x\\d\\d"),
        ("tng", "tng[1-7]x\\d\\d"),
    ),
    scope = ("choice", "major", "minor"),
):
    """
    Compose the dataset needed for this visualization. It may be published for D3 later.
    """
    themes_lu = themes_to_level(roots, -1)
    themes = set(t for t, (l, _) in themes_lu.iteritems())
    scores, totals = calculate_series_affinity_v1(themes, themesets, scope)
    color_lu = { t : c for t, c in zip(roots, colors) }
    maxtot = float(max(totals.itervalues()))
    s1, s2, s3 = [ x[0] for x in themesets ]

    font_min, font_max = 7.0, 14.0
    circle_min, circle_max = 6, 24
    sz_hi = 0
    radius_hi = 0

    for theme, data in scores.iteritems():
        sz = (totals[theme] / maxtot) ** 0.5
        radius = (totals[theme] / maxtot) ** 0.5
        sz_hi = max(sz_hi, sz)
        radius_hi = max(radius_hi, radius)

    ret = []

    for theme, data in scores.iteritems():
        x1 = data[s1]
        x2 = data[s2]
        x3 = data[s3]
        xx, yy = sym_rot_project(x3, x2, x1)
            
        sz = font_min + (totals[theme] / maxtot) ** 0.5 / sz_hi * (font_max - font_min)
        radius = circle_min + (totals[theme] / maxtot) ** 0.5 / radius_hi * (circle_max - circle_min)
        level, root = themes_lu[theme]
        color = color_lu[root]

        ret.append((
            level, root, theme, color, sz, radius,
            x1, x2, x3, xx, yy, 
        ))

    return ret


def do_make_metatheme_cube( 
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("#6F0F0F", "#176F0F", "#0F0F6F", "#6F5F0F"),
    themesets = (
        ("tos", "tos[0-3]x\\d\\d"), 
        ("tas", "tas[1-2]x\\d\\d"),
        ("tng", "tng[1-7]x\\d\\d"),
    ),
):
    '''
    Write an SVG image triangle of metathemes selected and color by arguments,
    positioned by relative affinities towards tos/tas/tng.
    '''
    viz_data = get_viz_data(roots, colors, themesets)

    svg = lib.svg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "12px",
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

    lines = []
    scale = 500.0
    origo = np.array([500, 500])
    textlines = []
    dotlines = []

    for row in viz_data:
        (level, root, theme, color, sz, radius, 
            x1, x2, x3, xx, yy) = row
        xx, yy = np.array([xx, yy]) * scale + origo
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
            sdata.text(xx, yy + sz / 2.5, theme, style = tstyle)
            sdata.circle(xx, yy, radius, style = cstyle)
        else:
            sdata.circle(xx, yy, 2, style = cstyle)

    np2o = sym_rot_project(0 * scale, 0 * scale, 1 * scale)
    np2a = sym_rot_project(0 * scale, 1 * scale, 0 * scale)
    np2n = sym_rot_project(1 * scale, 0 * scale, 0 * scale)
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

    for idx in xrange(3):
        pt = [np2o, np2a, np2n][idx]
        name = themesets[idx][0].upper()
        xx, yy = origo + pt * 1.02
        sgrid.line(ox, oy, xx, yy, markers = (None, "arrow"), cls = "axis")

        if xx < ox:
            align = "end"
            xx -= 10
        else:
            align = "start"
            yy -= 10

        sgrid.text(xx, yy, name, style = {"text-anchor": align})
    
    return svg


if __name__ == '__main__':
    #a = np.array([1,1,1], dtype=float)
    #print a
    #print rotate(a, -45, 0)

    svg = do_make_metatheme_cube()
    print svg.make(1600, 1600)

