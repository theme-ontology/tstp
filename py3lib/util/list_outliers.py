# Copyright 2021, themeontology.org
# Tests:
"""
Read the ontology from git checkout and report on some things that would seem like
red flags for one reason or another. For example, report here on stories that have
an excessive number of choice themes.
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
