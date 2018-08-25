"""
Read txt files with data in our special format and list items for which a given field is empty or missing.
"""
import sys
import os.path
import lib.dataparse
import lib.log


def main():
    target_field = sys.argv[2]
    topics = {}

    for arg in sys.argv[3:]:
        target = os.path.abspath(arg)
        stuff, notices = lib.dataparse.parse(target, {})

        for notice in notices:
            lib.log.error("%s: %s", target, notice)

        for topic, field, lines in stuff:
            matched = False
            if field == target_field:
                matched = any(l.strip() for l in lines)
            topics[topic] = topics.get(topic, False) or matched


    for topic, check in topics.iteritems():
        if not check:
            print topic


