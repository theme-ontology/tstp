# Copyright 2021, themeontology.org
# Tests:
"""
Read one or more text files and write their contents on stdout, while doing TO
specific cleaning and re-ordering.

Presently works only on story (.st.txt) files.
"""
import os.path
import credentials
import themeontology
import lib.log


def main():
    """
    Entry point.
    """
    path = os.path.join(credentials.GIT_THEMING_PATH, "notes")
    to = themeontology.read(path)
    for story in to.stories():
        nchoice = len(list(story.get("Choice Themes").iter_parts()))
        if nchoice > 5:
            lib.log.warn("[NChoice] Story '%s' has %s choice themes.", story.name, nchoice)
    to.write_clean()
