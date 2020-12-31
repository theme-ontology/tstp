"""
Merge different txt files with data in our special format together into one.
Some fields (themes, descriptions) will have predefined formating.
Priority is given to fields early in the list of files.
"""
import sys
import os.path
import lib.themeformat


def main():
    banned = set()
    forced = set()
    targets = set()

    for arg in sys.argv[2:]:
        if arg == "--all":
            allfields = True
        elif arg[:1] == "-":
            banned.add(arg[1:])
        elif arg[:1] == "+":
            forced.add(arg[1:])
        if arg[:1] in "-+":
            continue
        targets.add(os.path.abspath(arg))

    for line in lib.themeformat.format_files(sorted(targets), banned=banned, forced=forced):
        print line


