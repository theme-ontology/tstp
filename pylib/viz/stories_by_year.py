from __future__ import print_function
import lib.dataparse
import lib.log
import lib.mosvg
import lib.commits
import re
from collections import defaultdict
import numpy as np
import sys
import subprocess
import os.path

lib.log.redirect()


def get_data_from_head():
    """
    Get latest data about stories from db.
    Returns:

    """
    fromyear = 1890
    untilyear = 2020
    nn = untilyear - fromyear + 1
    xs = [fromyear + i for i in range(nn)]
    data = defaultdict(lambda: np.zeros(nn))
    themed = set()

    for storytheme in lib.dataparse.read_storythemes_from_db():
        themed.add(storytheme.name1)

    for story in lib.dataparse.read_stories_from_db():
        name = story.name
        date = story.date
        if name in themed:
            if 'collection' in name.lower() or re.match(r"\d{4}-\d{4}", date):
                continue
            if not re.match(r"\d{4}", date):
                continue
            year = int(date[:4])
            cat = re.match(r"([A-Za-z]+)", name).group(1)
            if fromyear <= year <= untilyear:
                data[cat][year - fromyear] += 1

    data = [ (np.sum(a), k, a) for k, a in data.items() ]
    data.sort(reverse=True)
    return xs, data


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


def limit_data(data, cutoff=19):
    protected = [ x for x in data if x[1] in ['play', 'novel', 'movie', 'nonfiction'] ]
    data = [ x for x in data if x[1] not in ['play', 'novel', 'movie', 'nonfiction'] ]
    remains = data[cutoff-len(protected):]
    data = data[:cutoff-len(protected)] + protected
    data.sort(reverse=True)
    if remains:
        ys = sum(x[2] for x in remains)
        data.append((0, 'miscellaneous', ys))
    return data


def make_viz_from_data(xs, data, yrange=None, bigtitle=None):
    nx1, ny1, nx2, ny2 = 50, 40, 950, 550
    maxarray = sum(rec[2] for rec in data)
    x1, x2 = xs[0] - 0.5, xs[-1] + 0.5
    y1, y2 = 0, round(np.max(maxarray)+5, -1)

    if yrange is not None:
        y2 = yrange

    svg = lib.mosvg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "10px",
            "fill": "black",
        },
        "rect.background": {
            "stroke": "black",
            "fill": "white",
        },
        "text.annotation": {
            "text-anchor": "middle",
            "font-size": "11px",
        },
        "text.title": {
            "text-anchor": "middle",
            "font-weight": "bold",
            "font-size": "11px",
        },
        "text.bigtitle": {
            "text-anchor": "end",
            "font-weight": "bold",
            "font-size": "16px",
            "color": "#666666",
        },
    })
    plot = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2, baseline_reference=10).config({
        'xtype': 'enum',
    })
    colorscale = iter_colors()
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    svg['annotation'].rect(lx0 - 5, ly0 - 5, 320, 10 + 15 * (len(data) / 4 + (1 if len(data)%4 else 0)), cls="background", style={"frill":"white"})
    svg['annotation'].text(nx1 + 10, ny1 - 10, "number of stories", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny2 + 25, "year of release", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "All Stories in Database by Year of Release", cls="title")

    if bigtitle:
        svg['annotation'].text(nx2, 30, bigtitle, cls="bigtitle")

    with plot.stack():
        for _, key, ys in data:
            skey = key
            if len(key) > 13:
                skey = key[:7] + ".." + key[-4:]
            color = next(colorscale)
            plot.plot([xs, ys], shape="bar", cls='', style={"fill":color})
            svg['annotation'].rect(lx, ly, 8, 8, style={"fill":color})
            svg['annotation'].text(lx + 12, ly+10, skey)
            lx += ldx
            if lx > lmaxx:
                lx = lx0
                ly += 15

    plot.plotarea()
    return svg, nx2 + nx1, ny2 + ny1


def make_viz():
    xs, data = get_data_from_head()
    data = limit_data(data)
    return make_viz_from_data(xs, data)


def make_animation(path):
    method = None
    gifs = []
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF, renderPM
        method = "svglib"
    except Exception as e:
        print("NO svglib", e)

    xs, data = get_data_from_head()
    data = limit_data(data)
    keys = set(r[1] for r in data)
    x0 = xs[0]
    xx = xs[-1]
    yrange = 80

    for row in data:
        print(row)

    def make(datapoint, key):
        aa = np.zeros(shape=len(xs))
        years = datapoint.get('prefix:{}'.format(key), {})
        for y, c in years.items():
            y = int(y)
            if x0 <= y <= xx:
                aa[y-x0] += c
            else:
                print("BAD YEAR:", y, c)
        return aa

    for atdt, datapoint in lib.commits.get_commits_data(period='weekly'):
        dtstr = atdt.date().isoformat()
        svgpath = path.format(dtstr)
        gifpath = path.format(atdt.date().isoformat()) + '.gif'
        gifs.append(gifpath)
        if os.path.isfile(gifpath):
            continue
        prefixes = {}
        zeros = np.zeros(shape=len(xs))
        for key in keys:
            prefixes[key] = make(datapoint, key)
        for pkey in datapoint:
            aa = np.zeros(shape=len(xs))
            if pkey.startswith("prefix:"):
                key = pkey.split(":", 1)[-1]
                if key not in prefixes:
                    aa += make(datapoint, key)
            prefixes['miscellanous'] = aa

        for idx, (_, key, _) in enumerate(list(data)):
            aa = prefixes.get(key, zeros)
            data[idx] = (sum(aa), key, aa)

        dd = data
        svg, width, height = make_viz_from_data(xs, dd, yrange=yrange, bigtitle=dtstr)
        svg.write(svgpath, width, height)
        print("WROTE", svgpath)

        if method == "svglib":
            drawing = svg2rlg(svgpath)
            renderPM.drawToFile(drawing, gifpath, fmt="GIF")
            print("WROTE", gifpath)

    if method:
        # convert -delay 2 -loop 0 tmp/*.gif -delay 1000 tmp/stories_2020-01-03.svg.gif test.gif
        outpath = path.format("animation") + ".gif"
        files = " ".join(gifs)
        cmd = "convert -delay 10 -loop 0 {} -delay 1000 {} {}".format(files, gifs[-1], outpath)
        print("RUNNING:", cmd)
        subprocess.call(cmd, shell=True)

def main():
    path = sys.argv[-1] if len(sys.argv) > 2 else 'test.svg'
    if any(x == '-A' for x in sys.argv):
        make_animation(path)
    else:
        svg, width, height = make_viz()
        svg.write(path, width, height)

















