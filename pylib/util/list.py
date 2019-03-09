import sys
from collections import defaultdict
import lib.dataparse
import lib.datastats
import csv


def all_themes_usage(tostream):
    graph = lib.datastats.get_theme_graph()
    records = defaultdict(lambda: [ 0 for _ in range(2) ])
    writer = csv.writer(tostream)

    for th in graph.nodes:
        records[th]

    for sth in lib.dataparse.read_storythemes_from_db():
        if sth.weight in ("major", "choice"):
            records[sth.name2][0] += 1
        elif sth.weight in ("minor",):
            records[sth.name2][1] += 1

    for th, rec in records.items():
        pstr = ', '.join(sorted(set(graph.parents_of(th))))
        astr = ', '.join(a for a in graph.ancestry_of(th) if a != th)
        rstr = ', '.join(sorted(set(graph.roots_of(th))))
        row = [str(x) for x in rec] + [th, pstr, rstr, astr]
        writer.writerow([x.encode("utf-8") for x in row])


def main():
    if "allthemesusage" in sys.argv:
        tostream = open(sys.argv[-1], "wb") if sys.argv.index("allthemesusage") < len(sys.argv) - 1 else sys.stdout
        all_themes_usage(tostream)
















