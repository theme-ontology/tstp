import lib.dataparse
import lib.log
import lib.mosvg
import re
from collections import defaultdict
import numpy as np
import sys

lib.log.redirect()


def main():
    path = sys.argv[-1] if len(sys.argv) > 2 else 'test.svg'
    svg, width, height = make_viz()
    svg.write(path, width, height)


def get_data():
    fromyear = 1890
    untilyear = 2020
    nn = untilyear - fromyear + 1
    xs = [ fromyear + i for i in xrange(nn) ]
    data = defaultdict(lambda: np.zeros(nn))

    for story in lib.dataparse.read_stories_from_db():
        name = story.name
        date = story.date
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


def make_viz():
    nx1, ny1, nx2, ny2 = 50, 40, 950, 550

    xs, data = get_data()
    maxarray = sum(rec[2] for rec in data)
    x1, x2 = xs[0] - 0.5, xs[-1] + 0.5
    y1, y2 = 0, round(np.max(maxarray)+5, -1)

    cutoff = 19
    protected = [ x for x in data if x[1] in ['play', 'novel', 'movie', 'nonfiction'] ]
    data = [ x for x in data if x[1] not in ['play', 'novel', 'movie', 'nonfiction'] ]
    remains = data[cutoff-len(protected):]
    data = data[:cutoff-len(protected)] + protected
    data.sort(reverse=True)

    if remains:
        ys = sum(x[2] for x in remains)
        data.append((0, 'miscellaneousmiscellaneousmiscellaneous', ys))

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
    })
    plot = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2).config({
        'xtype': 'enum',
    })
    colorscale = iter_colors()
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    svg['annotation'].rect(lx0 - 5, ly0 - 5, 320, 20 * len(data) / 4 - 10, cls="background", style={"frill":"white"})
    svg['annotation'].text(nx1 + 10, ny1 - 10, "number of stories", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny2 + 25, "year of release", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "All Stories in Database by Year of Release", cls="title")

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





