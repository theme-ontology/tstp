import os.path
import credentials
import lib.dataparse
import lib.files
import webobject


def list_all_objects():
    """
    Just list all theme, story, and storytheme objects in the main repository.
    """
    basepath = os.path.join(credentials.GIT_THEMING_PATH, "notes")

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$"):
        if path.endswith(".th.txt"):
            for themeobj in list(lib.dataparse.read_themes_from_txt(path, False)):
                print(themeobj)

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$"):
        if path.endswith(".st.txt"):
            for storyobj in list(lib.dataparse.read_stories_from_txt(path, False)):
                print(storyobj)

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$"):
        if path.endswith(".st.txt"):
            for storythemeobj in lib.dataparse.read_storythemes_from_txt(path, False):
                print(storythemeobj)


def make_theme_json():
    """
    Turn themes into some example json info.
    """
    basepath = os.path.join(credentials.GIT_THEMING_PATH, "notes")
    themeobjs = []
    allfields = set()

    for path in lib.files.walk(basepath, ".*\.(st|th)\.txt$"):
        if path.endswith(".th.txt"):
            themeobjs.extend(lib.dataparse.read_themes_from_txt(path, False))

    allfields = sorted(set(themeobjs[0].fields + themeobjs[0].extra_fields))
    print(webobject.Theme.make_json(themeobjs, allfields))
    print("FIELDS: %s" % allfields)




def main():
    make_theme_json()
    #list_all_objects()



