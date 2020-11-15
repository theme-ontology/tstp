from __future__ import print_function
import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
import urllib
import lib.datastats


log.set_logmode("binary")


TEMPLATE = """
<!DOCTYPE html><html><head>
    <meta charset="UTF-8">
    <title>Theme Hierarchy</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 0px;
            margin-bottom: 20em;
            padding: 1em;
        }
        h1 {
            background: #c0c0c0;
            border-bottom: 3px solid black;
            margin-top: 3em;
            margin-bottom: 0em;
        }
        h2 {
            margin-top: 0.75em;
            margin-bottom: 0.25em;
        }
        A {
            color: #000000;
            text-decoration: none;
        }
        A:hover {
            color: #CC0000;
            text-decoration: underline;
        }
        table {
            background: #f0f0f0;
            border-collapse: collapse;
        }
        th {
            background: #f0f0f0;
            border: 2px solid white;
        }
        td {
            background: #ffffff;
            border: 0px solid black;
            vertical-align: top;
        }
        div.headingbox {
            background: black;
            color: white;
            padding: 0.5em;
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
        }
    </style>
</head>
<body style="padding:0px;">
    <div class="container main-body headingbox">
        <div class="row"><H3>Theme Hierarchy Reference Sheet</H3></div>
    </div>
    <div class="container main-body">
        <div class="row">{CONTENT}</div>
    </div>
</body></html>
"""


def make_link(theme, display=None):
    theme = theme.encode("utf-8")
    url = "http://www.themeontology.org/theme.php?name=%s" % urllib.quote_plus(theme)
    display = display or theme
    return '<A href="%s">%s</A>' % (url, display)


def make():
    parents, children, lforder = lib.datastats.get_theme_tree()
    roots = sorted(th for th, thp in parents.iteritems() if len(thp) == 0)
    leafcount = {}
    arrow = u'\u2190'.encode("utf-8")
    lines = []

    for theme in lforder:
        for parent in parents[theme]:
            count = sum(leafcount.get(ch, 0) for ch in children[parent])
            count2 = sum(1 for ch in children[parent] if len(children[ch]) == 0)
            leafcount[parent] = count + min(1, count2)

    for root in roots:
        rootlink = make_link(root)
        lines.append("<H1>%s</H1>" % rootlink)

        for l2 in children[root]:
            pending = list(children[l2])
            l2link = make_link(l2)
            lines.append("  <H2>%s %s %s</H2>" % (rootlink, arrow, l2link))
            lines.append("  <TABLE>")

            while any(pending):
                pending, current = [], pending
                lines.append("<tr>")
                for theme in current:
                    if theme in leafcount:
                        nn = leafcount[theme]
                        lines.append("<th colspan=%s>%s</th>" % (nn, make_link(theme)))
                        pending.extend(th for th in children[theme] if children[th])
                        acc = [th for th in children[theme] if not children[th]]
                        if acc:
                            pending.append(tuple(acc))
                    else:
                        acc = theme
                        if isinstance(acc, tuple):
                            item = ", ".join(make_link(th) for th in acc[:4])
                            if len(acc) > 4:
                                item += ", ..."
                        else:
                            item = make_link(theme)
                        lines.append("<td>%s</td>" % item)
                        pending.append("")

                lines.append("</tr>")
            lines.append("  </TABLE>")
    return '\n'.join(lines)


def write_to_path(path):
    """
    :param path: Where to write the html data.
    """
    data = make()
    with open(path, "w") as fh:
        fh.write(TEMPLATE.replace("{CONTENT}", data))


def main():
    print(make())

