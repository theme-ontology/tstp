from __future__ import print_function
import urllib2
from bs4 import BeautifulSoup
import webdb
import sys
import webobject
import re
from natsort import natsorted


def main():
    fn = sys.argv[-1]
    urls = [
        "https://en.wikipedia.org/wiki/The_Decameron",
    ]
    tableclass = "wikitable sortable"
    stories = {}

    data = urllib2.urlopen(urls[0]).read()
    soup = BeautifulSoup(data, "html.parser")

    table = soup.find("table", class_=tableclass)
    for idx, row in enumerate(table.find_all("tr")):
        cells = row.find_all("td")
        if len(cells) >= 3:
            texts = [c.get_text() for c in cells]
            nday, nstory = [int(x) for x in re.match(r"\D*(\d+),\D*(\d+)", texts[0]).groups()]
            sid = "boccachio1353d{:02d}s{:02d}".format(nday, nstory)
            description = "Narrator: {}.\nLocation: {}.".format(*texts[1:3])
            if len(cells) >= 4 and texts[3].strip():
                description += "\nSubject: {}.".format(re.sub(r"\s*\[\d+\]\s*", "", texts[3]))
            stories[sid] = webobject.Story(
                name=sid,
                title="The Decameron: Day {}, Story {}".format(nday, nstory),
                description=description,
                date="1353",
            )
        else:
            print("SKIPPING ROW {}".format(idx))

    objs = [stories[sid] for sid in natsorted(stories)]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True, skip_fields=('collections',),
                                                 add_fields=("Ratings",), presorted=True)
    txt = txt.encode("utf-8")
    if fn.endswith(".txt"):
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
