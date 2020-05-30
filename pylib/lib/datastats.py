import json
import lib.dataparse
from lib.func import memoize
from collections import defaultdict, deque
from lib.graph import KWGraph


ROOTS = [
    "speculative fiction theme",
    "society",
    "the human condition",
    "the pursuit of knowledge",
]


@memoize
def get_theme_graph():
    graph = KWGraph()
    for theme in lib.dataparse.read_themes_from_db():
        child = theme.name
        parents = [t.strip() for t in theme.parents.split(",")]
        for parent in parents:
            if parent:
                graph.makeEdge(parent, child)
    graph.trimShortcuts()
    return graph



@memoize
def themes_with_usage():
    """
    Returns { theme_name => theme_object } where for each theme object th,
    th.stories is { story_name => storytheme_object }.
    """
    themes = list(lib.dataparse.read_themes_from_db())
    storythemes = list(lib.dataparse.read_storythemes_from_db())
    result = {}
    for th in themes:
        th.stories = {}
        result[th.name] = th
    for st in storythemes:
        th = result[st.name2]
        th.stories[st.name1] = st
    return result


@memoize
def stories_with_themes():
    """
    Returns { story_name => story_object } where for each story object st,
    st.stories is { theme_name => storytheme_object }.
    """
    stories = list(lib.dataparse.read_stories_from_db())
    storythemes = list(lib.dataparse.read_storythemes_from_db())
    result = {}
    for sobj in stories:
        sobj.themes = {}
        result[sobj.name] = sobj
    for st in storythemes:
        sobj = result[st.name1]
        sobj.themes[st.name2] = st
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
    Returns { 
        parents => [...], 
        children => [...],
        descriptions => { theme => description }
    }.
    """
    parents = []
    children = []
    descriptions = {}
    metas = {}
    for th in lib.dataparse.read_themes_from_db():
        thp = [x.strip() for x in th.parents.split(",")]
        if th.name == theme:
            parents = filter(None, thp)
            descriptions[th.name] = th.description
            metas[th.name] = json.loads(th.meta)
        elif theme in thp:
            children.append(th.name)
            descriptions[th.name] = th.description
            metas[th.name] = json.loads(th.meta)
    parents.sort()
    children.sort()
    return {
        "parents": parents,
        "children": children,
        "descriptions": descriptions,
        "metas": metas,
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
    return construct_theme_tree(lib.dataparse.read_themes_from_db())


def construct_theme_tree(themeobjects):
    """
    Given a list of theme objects:
    return (parents, children, lforder) as (
        { theme => [ parent1, parent2, ... ] },
        { theme => [ child1, child2, ... ] },
        [ t1, t2, ...],
    ) where t1, t2 is a reversed BFS.
    """
    parents = {}
    children = defaultdict(set)

    for thobj in themeobjects:
        theme = thobj.name
        thp = filter(None, [x.strip() for x in thobj.parents.split(",")])
        parents[theme] = sorted(set(thp))

        if theme not in children:
            children[theme] = set()

        for parent in parents[theme]:
            children[parent].add(theme)
            if parent not in parents:
                parents[parent] = []

    children = {k: sorted(v) for k, v in children.items()}

    leafs = [th for th, thc in children.items() if len(thc) == 0]
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
    return construct_metathemes_by_level(parents, children, bfs)


def construct_metathemes_by_level(parents, children, bfs, withLeaves=False, allRoots=False):
    """
    Return [ [L0 themes], [L1 themes], ...]
    """
    if allRoots:
        roots = [theme for theme in children if not parents.get(theme, [])]
    else:
        roots = ROOTS
    level = {t: 0 for t in roots}
    pending = roots
    changed = set()
    visited = set()  # guard against cycles

    while pending:
        for theme in pending:
            if theme not in visited:
                visited.add(theme)
                depth = level[theme] + 1
                for child in children[theme]:
                    level[child] = min(depth, level.get(child, depth))
                    changed.add(child)
        pending = list(sorted(changed))
        changed = set()

    result = []
    for theme, nn in level.items():
        if withLeaves or children.get(theme, []):
            while len(result) <= nn:
                result.append([])
            result[nn].append(theme)

    return result


def walk_children(theme, children, path):
    """
    Yields [t1, t2, ...] paths to all children in DF order.
    """
    path.append(theme)
    yield path

    for child in children[theme]:
        if child not in path:
            for p2 in walk_children(child, children, path):
                yield p2

    path.pop()


def all_pairs_shortest_path_to_common_parent(root, children, order, result):
    """
    Calculate all pairs' shortest path to a common parent.
        Exclude (t, t) = 1 by definition for all themes t.
        Exclude (t1, t2) iff t2 is listed before t1.
    """
    def _update_score(p1, p2, order, result):
        t1 = p1[-1]
        t2 = p2[-1]
        d1 = len(p1)
        d2 = len(p2)

        for tt in p1:
            if tt in p2:
                d1 = min(d1, len(p1) - p1.index(tt) - 1)
                d2 = min(d2, len(p2) - p2.index(tt) - 1)

        o1 = order[t1]
        o2 = order[t2]

        if o1 > o2:
            t1, t2 = t2, t1
            o1, o2 = o2, o1
            d1, d2 = d2, d1
        if (o1, o2) in result:
            dd1, dd2 = result[(o1, o2)]
            d1 = min(d1, dd1)
            d2 = min(d2, dd2)

        result[(o1, o2)] = (d1, d2)

    def _subtree_apspcp(c1, c2, children, order, result):
        for p1 in walk_children(c1, children, []):
            for p2 in walk_children(c2, children, []):
                _update_score(p1, p2, order, result)

    if root not in order:
        order[root] = len(order)

    for child in children[root]:
        all_pairs_shortest_path_to_common_parent(child, children, order, result)

    # score pairs whereof one is a direct descendant (one score is always 0)
    for pp in walk_children(root, children, []):
        _update_score([root], pp, order, result)

    # score pairs that are in different sub-trees
    for c1 in children[root]:
        for c2 in children[root]:
            if order[c1] > order[c2]:
                _subtree_apspcp(c1, c2, children, order, result)


@memoize
def get_themes_similarity_v1():
    """
    Return all pairs theme similarity measures.
    """
    (parents, children, lforder) = get_theme_tree()
    order = {}
    result = {}

    for theme, pl in parents.iteritems():
        if not pl:
            all_pairs_shortest_path_to_common_parent(theme, children, order, result)

    order = [ k for (k, v) in sorted(order.iteritems(), key = lambda x: x[-1]) ]
    scores = [ (k1, k2, v1, v2) for (k1, k2), (v1, v2) in result.iteritems() ]
    return order, scores


