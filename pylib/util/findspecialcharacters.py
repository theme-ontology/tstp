"""
Reads utf-8 text files and reports any characters that are a bit out of the ordinary.
"""
import sys
import log
import os
import glob
from collections import defaultdict


ACCEPTED = set(range(32, 127) + [10] + range(161, 256))


def find_special(line):
    special = set(ord(c) for c in line) - ACCEPTED
    return special


def main():
    counts = defaultdict(int)
    target = os.path.abspath(sys.argv[-1])
    log.info("reading files matching: " + target)

    for fpath in glob.glob(target):
        log.info("reading %s", fpath)
        with open(fpath, "r+") as fh:
            for idx, line in enumerate(fh):
                special = find_special(line.decode("utf-8"))
                if special:
                    log.warn("%s:%d:" % (fpath, idx) + ": FOUND ordinals: %s" % sorted(special))
                for d in special:
                    counts[d] += 1

    log.info("counts: %s" % sorted(counts.items()))
    sys.stderr.flush()
    for d, n in sorted(counts.items(), key=lambda x: -x[1]):
        print("%8d: %d" % (d, n))

