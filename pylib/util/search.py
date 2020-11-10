import sys
import lib.search


def main():
    idx, core = next((i, c) for i, c in enumerate(sys.argv) if c in lib.search.VALID_CORES)
    q = sys.argv[idx + 1]
    lib.search.DEBUG = '--debug' in sys.argv

    for s, w in lib.search.find(core, q):
        print s, w

