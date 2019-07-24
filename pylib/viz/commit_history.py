from __future__ import print_function
import lib.dataparse
import lib.log
import lib.mosvg
import re
from collections import defaultdict
import numpy as np
import sys
from credentials import GIT_THEMING_PATH_HIST
import os
import subprocess
import lib.files
import datetime
from dateutil.parser import parse
from lib.dates import iter_days


lib.log.redirect()

DEBUG = False


def get_datapoint(basepath):
    counts = defaultdict(set)
    data = defaultdict(float)

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$", 0):
        if path.endswith(".th.txt"):
            objs = list(lib.dataparse.read_themes_from_txt(path, False))
            counts["themes"].update(o.name for o in objs)
        if path.endswith(".st.txt"):
            objs = list(lib.dataparse.read_stories_from_txt(path, False))
            counts["stories"].update(o.name for o in objs)

    data["themes"] = len(counts["themes"])
    data["stories"] = len(counts["stories"])
    return data


def get_data():
    basepath = GIT_THEMING_PATH_HIST
    notespath = os.path.join(basepath, "notes")
    os.chdir(basepath)

    subprocess.check_output('git checkout HEAD'.split()).decode("utf-8")
    gitlog = subprocess.check_output('git log --no-merges --all'.split()).decode("utf-8")
    entries = []
    commit, author, date = None, None, None
    data = []

    for line in gitlog.split("\n"):
        if line.startswith("commit ") and not commit:
            commit = line.strip().split()[-1]
            author, date = None, None
        if line.startswith("Author: "):
            author = line.strip().split()[1]
        if line.startswith("Date: "):
            date = line[5:].strip()
        if not line.strip() and commit:
            entries.append((commit, author, parse(date, ignoretz=True)))
            commit, author, date = None, None, None

    entries.sort(key=lambda x: x[-1])
    dt1 = entries[0][-1]
    dt2 = entries[-1][-1]
    dtiter = iter_days(dt1, dt2, "fri", "00:00")
    # dtiter = iter_days("2019-07-01", dt2, "fri", "00:00") # debug
    atdt = next(dtiter)

    for idx, (commit, author, date) in enumerate(entries):
        if DEBUG:
            if date < parse("2018-12", ignoretz=True): continue # debug
            if len(data) > 60: break # debug
        while atdt < date:
            try:
                atdt = next(dtiter)
            except StopIteration:
                atdt = None
                break
        if atdt is None:
            break

        if idx < len(entries) - 1:
            if atdt >= entries[idx+1][-1]:
                continue
        # date must be the last viable date less than atdt
        print(date.isoformat(), commit)
        print("Evaluating for: {}...".format(atdt.isoformat()))
	res = None

        try:
            #res = subprocess.check_output(['git', 'checkout', commit], stderr=open(os.devnull, 'wb')).decode("utf-8")
            res = subprocess.check_output(['git', 'checkout', '-f', commit]).decode("utf-8")
        except Exception as e:
            print("GIT ERROR", e)
            print(res, "...")
            continue
        try:
            datapoint = get_datapoint(notespath)
            nthemes = datapoint["themes"]
        except:
            print("PARSE ERROR")
            continue
        if (nthemes > 500):
            data.append((atdt, datapoint))
            print(data[-1])

    return data


def draw_timeseries():
    data = get_data()
    d1 = min(x for x, _ in data)
    d2 = max(x for x, _ in data)
    xs = [ (x-d1).total_seconds() for x, _ in data ]
    ys_t = [ y["themes"] for _, y in data ]
    ys_s = [ y["stories"] for _, y in data ]
    nx1, ny1, nx2, ny2 = 50, 40, 950, 550
    x1, x2 = xs[0] - 0.5, xs[-1] + 0.5
    y1, y2 = min(min(ys_s), min(ys_t)), max(max(ys_s), max(ys_t))

    svg = lib.mosvg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "10px",
            "fill": "black",
        },
        'text.xtick' : {
            'opacity': '0.0',
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
        ".themesdata.datapoint": {
            'fill': '#cc6644',
        },
        ".themesdata.dataline": {
            'stroke-width': '2px',
            'stroke': '#cc6644',
        },
        ".storiesdata.datapoint": {
            'fill': '#884422',
        },
        ".storiesdata.dataline": {
            'stroke-width': '2px',
            'stroke': '#884422',
        },
    })
    plot = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2).config({
        'xtype': 'scalar',
    })
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    #svg['annotation'].rect(lx0 - 5, ly0 - 5, 320, 20 * len(data) / 4 - 10, cls="background", style={"frill":"white"})
    svg['annotation'].text(nx1 + 10, ny1 - 10, "count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny2 + 25, "time", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "All Themes/Stories Defined, by Time of Commit", cls="title")
    svg['annotation'].text(nx1 + 10, ny2 + 25, d1.date().isoformat(), cls="title")
    svg['annotation'].text(nx2 + 10, ny2 + 25, d2.date().isoformat(), cls="title", style={'text-anchor': 'end'})
    plot.plot([xs, ys_s], shape="line", cls='storiesdata', style={})
    plot.plot([xs, ys_t], shape="line", cls='themesdata', style={})
    plot.plotarea()

    return svg, nx2 + nx1, ny2 + ny1


def draw_story_theme_relation():
    data = get_data()

    xs = [ p['stories'] for _, p in data ]
    ys = [ p['themes'] for _, p in data ]
    labeldist = max(1, len(xs) / 10)
    labels = [ x.date().isoformat() if idx%labeldist==labeldist//2 else '' for idx, (x, _) in enumerate(data) ]

    nx1, ny1, nx2, ny2 = 50, 40, 950, 550
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    dx = xs[-1] - xs[0]
    dy = ys[-1] - ys[0]
    x1, x2 = x1 - dx*0.05, x2 + dx*0.05
    y1, y2 = y1 - dy*0.05, y2 + dy*0.05

    svg = lib.mosvg.SVG(style = {
        "text": {
            "font-family": "Helvetica",
            "font-size": "10px",
            "fill": "black",
        },
        '.plot text.xtick' : {
        },
        ".plot rect.background": {
            "stroke": "black",
            "fill": "white",
        },
        ".plot .datapoint": {
            'fill': '#ee8866',
        },
        ".plot text.datapointlabel": {
            'fill': '#000000',
            "font-weight": "bold",
        },
        ".plot .dataline": {
            'stroke-width': '3px',
            'stroke': '#ee8866',
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
        "line.manual": {
            "stroke": "#000000",
            "stroke-width": "1px",
        },
        "text.manual": {
            "stroke-width": "1px",
            "alignment-baseline": "hanging",
            "dominant-baseline": "hanging",
            "text-anchor": "middle",
        },
        "text.top": {
            "alignment-baseline": "baseline",
            "dominant-baseline": "baseline",
        },
    })
    svg['background'] #.rect(0, 0, 300, 300, style={"fill": "#cccccc", "fill-opacity": "0.9"})
    plot = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2).config({
        'xtype': 'scalar',
    })
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    svg['annotation'].text(nx1 + 10, ny1 - 10, "themes-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny2 + 25, "stories-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "All Themes/Stories Defined, relationship over time", cls="title")
    plot.plot([xs, ys, labels], shape="line", cls='story-theme-relation', style={})
    plot.plotarea()

    annotations = {
        "2018-12-22": "series: Futurama",
        "2019-03-15": "event: The Great Theme Purge",
        "2019-05-15": "series: Night Gallery",
        "2019-07-10": "series: Tales of the Unexpected",
    }
    done = set()
    ants = sorted((parse(k, ignoretz=True), v) for k, v in annotations.items())
    for idx, (dt, p) in enumerate(data):
        print(idx, (dt, p))
        if idx + 1 < len(data):
            dt2, p2 = data[idx + 1]
            for ii, (k, v) in enumerate(ants):
                if dt <= k and k < dt2:
                    if k not in done:
                        done.add(k)
                        t, v = v.split(": ", 1)
                        x0 = round(plot.v2x(p['stories']))
                        x1 = round(plot.v2x(p2['stories']))
                        xx = round(plot.v2x((p['stories'] + p2['stories']) // 2))
                        yy = plot.v2y((p['themes'] + p2['themes']) // 2)
                        if t == "series":
                            svg['background'].rect(x0, ny1, x1-x0, ny2-ny1, style={"fill": "#dddddd", "fill-opacity": "0.4"})
                            svg['background'].line(x0, ny1, x0, ny2, style={"stroke": "#dddddd", "fill-opacity": "0.8"})
                            svg['background'].line(x1, ny1, x1, ny2, style={"stroke": "#dddddd", "fill-opacity": "0.8"})
                            #svg['annotation'].line(xx, yy, xx, 500, cls="manual")
                            svg['annotation'].text(xx, 500, v, cls="manual")
                        if t == "event":
                            svg['annotation'].text(xx, yy-53, v, cls="manual top")

    return svg, nx2 + nx1, ny2 + ny1



def make_viz():
    return draw_story_theme_relation()


def main():
    imgpath = sys.argv[-1] if len(sys.argv) > 2 else 'test.svg'
    svg, width, height = draw_story_theme_relation()
    svg.write(imgpath, width, height)



