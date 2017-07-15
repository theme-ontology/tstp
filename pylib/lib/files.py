import os
import os.path
import re


def walk(path, pattern = ".*", levels = -1):
    """
    Find files whose name matches a pattern up to a given depth.
    """
    r = re.compile(pattern)

    # yield matching files
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isfile(spath) and r.match(item):
            yield spath

    # recurse
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isdir(spath) and levels != 0:
            for res in walk(spath, pattern, levels - 1):
                yield res

