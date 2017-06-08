from collections import defaultdict
import webobject


SUPPORTED_OBJECTS = {
    "storydefinitions": webobject.Story,
    "themedefinitions": webobject.Theme,
    "storythemes": webobject.StoryTheme,
}


def get_metatheme_data():
    """
    Returns
    -------
    leaf_data: { leaf_theme => [(sid1, weight1), ...], ...},
    meta_data: { meta_theme => [(sid1, weight1), ...], ...},
    parents: { theme => [parent1, ...] },
    toplevel: [ theme1, ...],
    """
    themes = webobject.Theme.load()
    storythemes = webobject.StoryTheme.load()
    parent_lu = {}
    child_lu = defaultdict(set)
    toplevel = set()
    meta_data = defaultdict(set)
    leaf_data = defaultdict(set)
    ret_meta_data = {}
    ret_leaf_data = {}
    ret_child_lu = {}

    for theme in themes:
        parents = [ t.strip() for t in theme.parents.split(",") ]
        parent_lu[theme.name] = parents

        for parent in parents:
            child_lu[parent].add(theme.name)

    for st in storythemes:
        theme = st.name2
        theme_stack = [ theme ]
        item = (st.name1, st.weight)
        leaf_data[theme].add(item)
        first = True

        while theme_stack:
            theme = theme_stack.pop()

            if not first:
                meta_data[theme].add(item)

            first = False

            if theme in parent_lu:
                theme_stack.extend(parent_lu[theme])
            else:
                toplevel.add(theme)

    for key, items in meta_data.iteritems():
        ret_meta_data[key] = sorted(items)

    for key, items in leaf_data.iteritems():
        ret_leaf_data[key] = sorted(items)

    for key, items in child_lu.iteritems():
        ret_child_lu[key] = sorted(items)

    toplevel = sorted(toplevel)
    return ret_leaf_data, ret_meta_data, parent_lu, ret_child_lu, toplevel


def get_defenitions(target):
    """
    Returns
    -------
    [ (...), ... ]
    Table rows with the headers in the first row.
    """
    klass = SUPPORTED_OBJECTS[target]
    remap = {
        "name": target[:5],
        "name1": "story",
        "name2": "theme",
    }
    
    objs = klass.load()
    headers = [ f for f in klass.fields if "category" not in f ]
    rows = [ [remap.get(f, f) for f in headers] ]
    
    for obj in objs:
        row = []
        for field in headers:
            row.append(unicode(getattr(obj, field)).encode("utf-8"))
        rows.append(row)

    return rows


if __name__ == '__main__':
    get_metatheme_data()



