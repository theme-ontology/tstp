import webdb
from lib.wikiparsers import fetch_links_info
import sys


def main():
    fn = sys.argv[-1]
    urls = [
        "https://en.wikipedia.org/wiki/List_of_Aesop%27s_Fables",
    ]
    stories = {}

    data = fetch_links_info(urls[0])
    return


    objs = [stories[sid] for sid in sorted(stories)]
    txt = webdb.get_defenitions_text_for_objects(objs, empty_storythemes_headers=True, skip_fields=('collections',),
                                                 add_fields=("Ratings",))
    txt = txt.encode("utf-8")
    if fn.endswith(".txt"):
        with open(fn, "wb+") as fh:
            fh.write(txt)
    else:
        # this fucking breaks on fucking windows with fucking unicode sometimes
        sys.stdout.write(txt)
