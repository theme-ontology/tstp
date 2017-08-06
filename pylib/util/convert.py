import sys
import os
import webdb
import lib.dataparse


def main():
    method = sys.argv[-2]
    target = os.path.abspath(sys.argv[-1])
    objs = []

    if method == "themedefs":
        m1 = "themes"
    elif method == "storydefs":
        m1 = "stories"
    elif method == "storythemes":
        m1 = "storythemes"

    if target == "<localdb>":
        m2 = 'db'
    elif target.endswith(".txt"):
        m2 = 'txt'
    elif target.endswith(".xls"):
        if method == "storythemes":
            m2 = 'xls_compact'
        else:
            m2 = 'xls'

    attr = "read_%s_from_%s" % (m1, m2)
    func = getattr(lib.dataparse, attr)
    objs = list(func() if m2 == "db" else func(target))
    txt = webdb.get_defenitions_text_for_objects(objs)

    print txt.encode("utf-8")
