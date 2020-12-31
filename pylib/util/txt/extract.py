# Copyright 2020, themeontology.org
# Tests:
"""
Takes a list of themes, extracts those theme defenitions
from a .th.txt file and writes to two separate new .th.txt files.
"""
import sys
import os.path
import lib.themeformat
import codecs


def main():
    themes = sys.argv[2:-3]
    inputfile = sys.argv[-3]
    file1 = sys.argv[-2]
    file2 = sys.argv[-1]
    retained, extracted = lib.themeformat.format_files([os.path.abspath(inputfile)], extract=themes)
    with codecs.open(file1, "w", encoding='utf-8') as fh:
        fh.write("\n".join(retained) + "\n")
    with codecs.open(file2, "w", encoding='utf-8') as fh:
        fh.write("\n".join(extracted) + "\n")


