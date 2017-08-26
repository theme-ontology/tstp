import lib.dataparse


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

    return {
        "parents": parents,
        "children": children,
    }


