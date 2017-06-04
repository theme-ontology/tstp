import urllib
import json
import operator as op
from collections import deque
from collections import defaultdict

from scipy.stats import hypergeom
import numpy as np

import func
import svg
import log


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
    return r[0], r[1]


def norm(v):
    return v.dot(v) ** 0.5


def phyper(k, K, n, N):
    return 1.0 - hypergeom.cdf(k - 1, N, n, K)


@func.memoize
def get_data():
    url = BASE_URL + "action=metathemedata"
    response = urllib.urlopen(url)
    ret_data = json.loads(response.read())
    return ret_data


def themes_to_level(roots, level):
    """
    @returns
        { theme1 => (level1, root1), ... }
    """
    data, parent_lu, toplevel = get_data()
    child_lu = defaultdict(list)

    for theme, parents in parent_lu.iteritems():
        for parent in parents:
            child_lu[parent].append(theme)

    thlevel = { th: 0 for th in roots }
    throot = { th: th for th in roots }
    remain = deque(roots)

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
    data, parent_lu, toplevel = get_data()
    tos, tas, tng = 'tos tas tng'.split()
    tosc, tasc, tngc = 80, 22, 178
    nc = tosc + tasc + tngc
    scope = ("minor", "major")
    counts = defaultdict(lambda: defaultdict(float))

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
        tot = sum(x for x in counts[theme].itervalues())
        for series, seriesc in zip((tos, tas, tng), (tosc, tasc, tngc)):
            count = counts[theme][series]
            pvalue = phyper(count, seriesc, tot, nc)
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
            
    return scores2




def do_make_metatheme_cube( 
    level = 3, 
    roots = ('the human condition', 'society', 'the pursuit of knowledge', 'alternate reality'),
    colors = ("rgb(166,85,84)", "rgb(107,140,84)", "rgb(11,112,156)", "rgb(156,122,26)"),
):
    '''
    Write an SVG image triangle of metathemes selected and color by arguments,
    positioned by relative affinities towards tos/tas/tng.
    '''
    themes_lu = themes_to_level(roots, level)
    themes = set(themes_lu)
    scores = calculate_series_affinity_v1(themes)
    color_lu = { t : c for t, c in zip(roots, colors) }
    totals = { theme: sum(scores[theme].values()) for theme in scores }

    maxtot = float(max(totals.itervalues()))
    mintot = float(min(totals.itervalues()))
    dtot = (maxtot - mintot)

    style = '''
        text {
            font-family:  Helvetica;
            font-size:    8px;
            fill:         #333333;
            text-anchor:  middle;
        }
        polyline {
            stroke:       #333333;
            stroke-width: 4px;
            fill-opacity: 0.1;
        }
    '''
    tos, tas, tng = 'tos tas tng'.split()
    
    # make drawing
    lines = []
    scale = 800.0
    
    font_min = 14.0
    circle_min = 10
    
    lines.append('''<g transform="translate(800, 800) rotate(00)"> ''')
    
    dotlines = []
    textlines = []

    for kw, data in scores.iteritems():
        color = color_lu[themes_lu[kw][1]]
            
        x1 = data[tng] * scale
        x2 = data[tas] * scale
        x3 = data[tos] * scale
        xx, yy = sym_rot_project(x1, x2, x3)
            
        sz = font_min + (totals[kw] / maxtot) ** 0.5 * 10.0 * 4 / len(roots)
        radius = circle_min + (totals[kw] / maxtot) ** 0.5 / len(roots) * 100
        print kw, totals[kw], radius
        
        textlines.append('''  <g transform="translate(%s, %s) rotate(-00) "> ''' % (xx, yy + sz / 2.5) )
        textlines.append('''    <text style="fill: %s; font-size:%spx;" x="%s" y="%s">%s</text>''' % (color, sz, 0, 0, kw) )
        textlines.append('''  </g> ''')
        dotlines.append('''  <g transform="translate(%s, %s) rotate(-00) "> ''' % (xx, yy) )
        dotlines.append('''    <circle style="fill: %s; stroke: %s; fill-opacity:0.5; stroke-opacity:0.7;" x="%s" y="%s" r="%s"/>''' % (color, color, 0, 0, radius) )
        dotlines.append('''  </g> ''')

    for v in [
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]:
        x1, x2, x3 = v
        xx, yy = sym_rot_project(x1 * scale, x2 * scale, x3 * scale)
        kw = ''.join(str(x) for x in v)
        color = '#000000' 
        sz = 10
        radius = 10
        textlines.append('''  <g transform="translate(%s, %s) rotate(-00) "> ''' % (xx, yy + sz / 2.5) )
        textlines.append('''    <text style="fill: %s; font-size:%spx;" x="%s" y="%s">%s</text>''' % (color, sz, 0, 0, kw) )
        textlines.append('''  </g> ''')
        color = '#ff0000' 
        dotlines.append('''  <g transform="translate(%s, %s) rotate(-00) "> ''' % (xx, yy) )
        dotlines.append('''    <circle style="fill: %s; stroke: %s; fill-opacity:0.5; stroke-opacity:0.7;" x="%s" y="%s" r="%s"/>''' % (color, color, 0, 0, radius) )
        dotlines.append('''  </g> ''')
        
    lines.extend(dotlines)
    lines.extend(textlines)

    lines.append('''</g>''')
    
    # write to file
    svgdata = svg.make_svg(1600, 1600, style, '\n'.join(lines))
    filename = "D:\\Temp\\test.svg"
    log.info( 'Writing: %s' % filename ) 
    with open(filename, "w+") as fh:
        fh.write(svgdata.encode("utf-8"))


if __name__ == '__main__':
    do_make_metatheme_cube()




