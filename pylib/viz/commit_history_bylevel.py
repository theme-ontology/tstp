from __future__ import print_function
from collections import defaultdict
import lib.log
import sys
import lib.files
from viz.commit_history import get_data, story_theme_base, annotate_storytheme


lib.log.redirect()


def draw_story_leveltheme_relation():
    """
    One curve for each theme level, count of themes (at each level) shown against
    count of stories.
    Returns:
    svg, width, height
    """
    data = get_data()
    xs = [p['stories'] for _, p in data]
    xs2 = [p['themedstories'] for _, p in data]
    labeldist = max(1, len(xs) / 10)
    labels = [x.date().isoformat() if idx % labeldist == labeldist // 2 else '' for idx, (x, _) in enumerate(data)]
    ysByLevel = []
    for nn in range(6):
        ysByLevel.append([p['themesL%s' % nn] for _, p in data])
    ysDeepLevel = [p['themesLP'] for _, p in data]
    curves = ysByLevel + [ysDeepLevel]
    names = ["Level:%s"%i for i, _ in enumerate(ysByLevel)] + ["Level:6+"]
    levelcolors = [
        "#726abd", "#8ad745", "#9f45d8", "#d4bc53", "#5b7181",
        "#d0533a", "#96c8ca", "#a47453", "#cd9ec0", "#5e8143",
    ]
    cutoff = 150
    midn = len(xs2) / 2
    nx1, ny1, nx2, ny2 = 50, 40, 950, 380
    ny3, ny4 = 400, 660
    x1, x2 = min(xs2), max(xs)
    y1, y2 = 0, max(max(ys[-midn:]) for ys in curves)
    y3 = max(y for y in [max(ys[-midn:]) for ys in curves] if y < cutoff)
    dx = xs[-1] - xs[0]
    dy = y2 - y1
    x1, x2 = x1 - dx*0.05, x2 + dx*0.05
    y1 = 0
    y2 += (y2 - y1) * 0.05
    y3 += (y3 - y1) * 0.05

    svg = story_theme_base()
    plot1 = svg["chart"].xychart(nx1, ny1, nx2, ny2,  x1, x2, y1, y2).config({'xtype': 'scalar'})
    plot2 = svg["chart"].xychart(nx1, ny3, nx2, ny4,  x1, x2, y1, y3).config({'xtype': 'scalar'})
    plotassign = {nn: plot1 if max(ys[-midn:]) >= cutoff else plot2 for nn, ys in enumerate(curves)}
    lx0, ly0, ldx, lmaxx = nx1 + 10, ny1 + 10, 80, 320
    lx, ly = lx0, ly0
    svg['annotation'].text(nx1 + 10, ny1 - 10, "themes-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, ny4 + 25, "stories-count", cls="annotation")
    svg['annotation'].text((nx1 + nx2) / 2, 20, "Themes By Level vs. Stories, over time", cls="title")
    for nn, ys in enumerate(curves):
        plotassign[nn].plot([xs, ys], shape="line", cls='story-leveltheme', style={'stroke': '#cccccc'})
    for nn, ys in enumerate(curves):
        color = levelcolors[nn]
        plotassign[nn].plot([xs2, ys], shape="line", cls='story-leveltheme', style={'stroke': color})
    plotassign[3].plot([xs2, curves[3], labels], shape="line", cls='date-labels', style={})
    plot1.plotarea()
    plot2.plotarea()
    annotate_storytheme(svg, plot1, data, ny1, ny2, texty=100)
    annotate_storytheme(svg, plot2, data, ny3, ny4, texty=-1)

    crowding = defaultdict(int)
    for nn, (curve, name) in enumerate(zip(curves, names)):
        yy = plotassign[nn].v2y(curve[-1]) - 10
        ybin = yy // 6
        cwd = max(crowding[ybin], crowding[ybin - 1])
        if cwd % 2 == 0:
            xx = nx2 - 70 - 62 * (cwd // 2)
        else:
            xx = nx1 + 5 + 62 * (cwd // 2)
        crowding[ybin - 1] += 1
        crowding[ybin] += 1
        svg['annotation'].rect(xx, yy, 65, 12, cls="background", style={
            "fill": "white", "stroke": "rgba(0,0,0,0.5)", "opacity": "0.5"})
        color = levelcolors[nn]
        svg['annotation'].rect(xx + 10, yy + 2, 8, 8, style={"fill": color})
        svg['annotation'].text(xx + 20, yy + 10, name)

    svg['annotation'].rect(nx1 + 5, ny3 + 5, 150, 20, cls="background", style={
        "fill": "white", "stroke": "rgba(0,0,0,0.5)"})
    svg['annotation'].rect(nx1 + 15, ny3 + 11, 8, 8, style={"fill": "#cccccc"})
    svg['annotation'].text(nx1 + 25, ny3 + 19, "includes unthemed stories")
    return svg, nx2 + nx1, ny4 + ny1


def make_viz():
    """
    Entry point.
    """
    return draw_story_leveltheme_relation()


def main():
    """
    Entry point.
    """
    imgpath = sys.argv[-1] if len(sys.argv) > 2 else 'test.svg'
    svg, width, height = draw_story_leveltheme_relation()
    svg.write(imgpath, width, height)



