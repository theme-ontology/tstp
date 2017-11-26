import lib.dataparse
from lib.func import memoize
from collections import defaultdict, deque


ROOTS = [
    "alternate reality",
    "society",
    "the human condition",
    "the pursuit of knowledge",
]


@memoize
def themes_with_usage():
    """
    Returns { theme_name => theme_object } where for each theme object th,
    th.stories is { story_name => storytheme_object }.
    """
    themes = list(lib.dataparse.read_themes_from_db())
    storythemes = list(lib.dataparse.read_storythemes_from_db())
    result = { t.name : t for t in themes }

    for th in themes:
        th.stories = {}
        result[th.name] = th

    for st in storythemes:
        th = result[st.name2]
        th.stories[st.name1] = st

    return result


@memoize
def metathemes_with_usage():
    """
    Returns { theme_name => [ sid1, sid2, ... ] } for all themes that have
    at least one child.
    """
    parents_lu, children_lu, lforder = lib.datastats.get_theme_tree()
    themes_lu = lib.datastats.themes_with_usage()
    levels = lib.datastats.get_metathemes_by_level()
    result = {}

    for level, themes in enumerate(levels):
        for theme in themes:
            children = deque(children_lu[theme])
            visited = set(children)
            stories = dict(themes_lu[theme].stories)

            while children:
                child = children.popleft()
                stories.update(themes_lu[child].stories)

                for cc in children_lu[child]:
                    if cc not in visited:
                        children.append(cc)
                        visited.add(cc)

            result[theme] = stories

    return result


@memoize
def get_theme_stats(theme):
    """
    Returns { parents => [...], children => [...] }.
    """
    parents = []
    children = []

    for th in lib.dataparse.read_themes_from_db():
        thp = [ x.strip() for x in th.parents.split(",") ]
        if th.name == theme:
            parents = filter(None, thp)
        elif theme in thp:
            children.append(th.name)

    parents.sort()
    children.sort()
    
    return {
        "parents": parents,
        "children": children,
    }


@memoize
def get_theme_tree():
    """
    return (parents, children, lforder) as (
        { theme => [ parent1, parent2, ... ] },
        { theme => [ child1, child2, ... ] },
        [ t1, t2, ...],
    ) where t1, t2 is a reversed BFS.
    """
    parents = {}
    children = defaultdict(set)

    for thobj in lib.dataparse.read_themes_from_db():
        theme = thobj.name
        thp = filter(None, [ x.strip() for x in thobj.parents.split(",") ])
        parents[theme] = sorted(set(thp))

        if theme not in children:
            children[theme] = set()

        for parent in parents[theme]:
            children[parent].add(theme)
            if parent not in parents:
                parents[parent] = []

    children = { k : sorted(v) for k, v in children.iteritems() }

    leafs = [ th for th, thc in children.iteritems() if len(thc) == 0 ]
    lforder = []
    qq = deque(leafs)
    ss = set()

    while qq:
        theme = qq.popleft()
        lforder.append(theme)
        
        for parent in parents[theme]:
            if parent not in ss:
                qq.append(parent)
                ss.add(parent)

    return parents, children, lforder


@memoize
def get_metathemes_by_level():
    """
    Return all themes that are parents as:
    [ 
        [root1, root2, ...], 
        [l1theme1, l2theme2, ...], 
        [l2theme1, ...], 
        ... 
    ]
    """
    parents, children, bfs = get_theme_tree()
    level = {}
    result = []

    for theme in reversed(bfs):
        if children[theme]:
            ps = parents[theme]
            pl = max(level.get(t, -1) for t in ps) if ps else -1
            nn = max(level.get(theme, 0), pl + 1)

            if nn > 0 or theme in ROOTS:
                level[theme] = nn

    themes = sorted(level.iteritems(), key = lambda x: (x[1], x[0]))

    for theme, nn in themes:
        while len(result) <= nn:
            result.append([])
        result[nn].append(theme)

    return result

