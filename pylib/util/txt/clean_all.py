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


def main():
    """
    Entry point.
    """
    path = os.path.join(credentials.GIT_THEMING_PATH, "notes")
    to = themeontology.read(path)
    to.write_clean()
