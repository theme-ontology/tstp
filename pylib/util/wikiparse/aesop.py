from __future__ import print_function
import urllib2
from bs4 import BeautifulSoup
import webdb
from lib.wikiparsers import fetch_links_info
import sys
import webobject
import re


def orderpredicate(sid):
    items = list(reversed(re.split("(\d+)", sid)))
    items[1] = int(items[1])
    return tuple(items)


def main():
    fn = sys.argv[-1]
    urls = [
        "https://en.wikipedia.org/wiki/The_Decameron",
    ]
    stories = {}

    for title, pagename, data in fetch_links_info(urls[0], startafter="/wiki/Aesop$", stopat="/wiki/Template:Aesop$"):
        if pagename in fails:
            sid = "aesop{:02d}un".format(failcount)
            failcount += 1
        else:
            pi = None
            for pattern in perrypatterns:
                if not pi:
                    pi = re.search(pattern, data["extract"])
            if not pi:
                page = urllib2.urlopen(data["content_urls"]["mobile"]["page"]).read()
                soup = BeautifulSoup(page, "html.parser")
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                text = " ".join(x for x in lines if x)
                for pattern in perrypatterns:
                    if not pi:
                        pi = re.search(pattern, text)
            if not pi:
                print("FAIL: ", title, pagename)
            sid = "aesop{:03d}pi".format(int(pi.group(1)))
        stories[sid] = webobject.Story(
            name=sid,
            title=title,
            description=data["extract"],
            date="564 BC",
        )

    objs = [stories[sid] for sid in sorted(stories, key=orderpredicate)]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True, skip_fields=('collections',),
                                                 add_fields=("Ratings",), presorted=True)
    txt = txt.encode("utf-8")
    if fn.endswith(".txt"):
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
