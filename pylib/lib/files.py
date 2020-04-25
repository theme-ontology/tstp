import os
import os.path
import re
import credentials


def safe_filename(unsafe):
    """
    Turn an unsafe string into something that ought to be a nice safe filename on both linux and windows.
    """
    maxlength = 50
    keepcharacters = ('.', '_')
    unsafe = re.sub(r"[ \(\)]+", "_", unsafe)
    return "".join(c for c in unsafe if c.isalnum() or c in keepcharacters).rstrip()[:maxlength].strip("_")


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


def mkdirs(path):
    """
    Make dir including parent dirs if they do not exist.
    """
    if not os.path.isdir(path):
        os.makedirs(path)


def preparefile(path):
    """
    A ensure that the base path exists by creating it if needed. Then check if file exists.

    Args:
        path: path fo a file.

    Returns:
    Return True if the file does not exist, False if it does.
    """
    if not path:
        return False
    basepath = os.path.split(path)[0]
    mkdirs(basepath)
    return not os.path.isfile(path)


def path2url(path):
    """
    Take a local path and convert it to a url by which the object is
    accessible, assuming it lies in the public dir.
    Returns: url
    """
    basepath = os.path.join(credentials.PUBLIC_DIR, "m4")
    if path.startswith(basepath):
        urlobj = path[len(basepath):].replace("\\", "/").strip("/")
        return credentials.SERVER_PUB_URL + "m4/" + urlobj
    return ""

