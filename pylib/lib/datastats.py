import lib.dataparse
from collections import defaultdict, deque


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
