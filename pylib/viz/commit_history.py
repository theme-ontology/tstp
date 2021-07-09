from __future__ import print_function
import lib.dataparse
import lib.log
import lib.mosvg
import sys
import lib.files
from dateutil.parser import parse
from lib.commits import get_commits_data
import textwrap


lib.log.redirect()


def get_data():
    return get_commits_data()


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


def story_theme_base():
    """
    Set up a chart for #stories on x, and #themes on y.
    Returns:
    lib.mosvg.SVG type
    """
    svg = lib.mosvg.SVG(style={
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
        ".plot .story-theme-relation.datapoint": {
            'fill': '#bbbbbb',
        },
        ".plot .themedstory-theme-relation.datapoint": {
            'fill': '#ee8866',
        },
        ".plot .date-labels.datapoint": {
            'visibility': 'hidden',
        },
        ".plot text.datapointlabel": {
            'fill': '#000000',
            "font-weight": "bold",
        },
        ".plot .story-theme-relation.dataline": {
            'stroke-width': '3px',
            'stroke': '#bbbbbb',
        },
        ".plot .themedstory-theme-relation.dataline": {
            'stroke-width': '3px',
            'stroke': '#ee8866',
        },
        ".plot .date-labels.dataline": {
            'visibility': 'hidden',
        },
        ".plot .story-leveltheme.dataline": {
            'stroke-width': '2px',
        },
        ".plot .story-leveltheme.datapoint": {
            'visibility': 'hidden',
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
    svg['background']
    return svg


def annotate_storytheme(svg, plot, data, ny1, ny2, texty=500):
    annotations = {
        "2018-12-22": "series: Futurama",
        "2019-03-15": "event: The Great Theme Purge",
        "2019-05-15": "series: Night Gallery",
        "2019-07-10": "series: Tales of the Unexpected",
        "2019-11-05": "series: The Twilight Zone (1985)",
        "2020-04-12": "series: The Twilight Zone (1959)",
        "2020-09-18": "series: Alfred Hitchcock Presents",
        "2021-01-10": "series: Aesop's Fables",
        "2021-07-06": "event: The Greater Theme Purge",
    }
    done = set()
    ants = sorted((parse(k, ignoretz=True), v) for k, v in annotations.items())
    for idx, (dt, p) in enumerate(data):
        if idx + 1 < len(data):
            dt2, p2 = data[idx + 1]
            for ii, (k, v) in enumerate(ants):
                if dt <= k and k < dt2:
                    if k not in done:
                        done.add(k)
                        t, v = v.split(": ", 1)
                        title = "\n".join(textwrap.wrap(v, 12))
                        x0 = round(plot.v2x(p['stories']))
                        x1 = round(plot.v2x(p2['stories']))
                        xx = round(plot.v2x((p['stories'] + p2['stories']) // 2))
                        yy = plot.v2y((p['themes'] + p2['themes']) // 2)
                        if t == "series":
                            svg['background'].rect(x0, ny1, x1-x0, ny2-ny1, style={"fill": "#dddddd", "fill-opacity": "0.4"})
                            svg['background'].line(x0, ny1, x0, ny2, style={"stroke": "#dddddd", "fill-opacity": "0.8"})
                            svg['background'].line(x1, ny1, x1, ny2, style={"stroke": "#dddddd", "fill-opacity": "0.8"})
                            if texty >= 0:
                                svg['annotation'].text(xx, texty, title, valign=1.0, cls="manual")
                        if t == "event" and texty >= 0:
                            svg['annotation'].text(xx, yy-53, title, cls="manual top")


def draw_story_theme_relation():
    """
    One curve for stories defined and one for themed stories, count of themes shown against
    count of stories.
    Returns:
    svg, width, height
    """
    data = get_data()
    xs = [ p['stories'] for _, p in data ]
    xs2 = [ p['themedstories'] for _, p in data ]
    ys = [ p['themes'] for _, p in data ]
    labeldist = max(1, len(xs) / 10)
    labels = [x.date().isoformat() if idx % labeldist == labeldist // 2 else '' for idx, (x, _) in enumerate(data)]
    nx1, ny1, nx2, ny2 = 50, 40, 950, 550
    x1, x2 = min(xs2), max(xs)
    y1, y2 = min(ys), max(ys)
    dx = xs[-1] - xs[0]
    dy = y2 - y1
    x1, x2 = x1 - dx*0.05, x2 + dx*0.05
    y1, y2 = y1 - dy*0.05, y2 + dy*0.05

    svg = story_theme_base()
    plot = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2).config({
        'xtype': 'scalar',
    })
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    svg['annotation'].text(nx1 + 10, ny1 - 10, "themes-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny2 + 25, "stories-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "All Themes/Stories Defined, relationship over time", cls="title")
    plot.plot([xs, ys], shape="line", cls='story-theme-relation', style={})
    plot.plot([xs2, ys], shape="line", cls='themedstory-theme-relation', style={})
    plot.plot([xs2, ys, labels], shape="line", cls='date-labels', style={})
    plot.plotarea()
    annotate_storytheme(svg, plot, data, ny1, ny2)

    # draw legend
    svg['annotation'].rect(nx1 + 5, ny1 + 5, 120, 40, cls="background", style={
        "fill": "white", "stroke": "rgba(0,0,0,0.5)"})
    svg['annotation'].rect(nx1 + 15, ny1 + 15, 8, 8, style={"fill": "#bbbbbb"})
    svg['annotation'].text(nx1 + 25, ny1 + 22, "stories defined")
    svg['annotation'].rect(nx1 + 15, ny1 + 25, 8, 8, style={"fill": "#ee8866"})
    svg['annotation'].text(nx1 + 25, ny1 + 32, "stories themed")

    return svg, nx2 + nx1, ny2 + ny1


def make_viz():
    """
    Entry point.
    """
    return draw_story_theme_relation()


def write_data(filename):
    """
    Write the data as xls to a file.
    """
    data = get_data()
    xs = [ p['themedstories'] for _, p in data ]
    ys = [ p['themes'] for _, p in data ]
    labels = [x.date().isoformat() for idx, (x, _) in enumerate(data)]
    import pandas as pd
    df = pd.DataFrame({
        "themed_stories": xs,
        "defined_themes": ys,
    }, columns=["themed_stories", "defined_themes"], index=labels)
    print(df)
    df.to_excel(filename)
    return


def main():
    """
    Entry point.
    """
    filename = sys.argv[-1] if len(sys.argv) > 2 else 'test.svg'
    if filename.endswith(".xlsx"):
        write_data(filename)
    else:
        svg, width, height = draw_story_theme_relation()
        svg.write(filename, width, height)



