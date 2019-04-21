"""
Merge different txt files with data in our special format together into one.
Some fields (themes, descriptions) will have predefined formating.
Priority is given to fields early in the list of files.
"""
import sys
import os
import lib.dataparse
import lib.xls
from collections import defaultdict
import lib.log
import glob
import codecs


THEME_FIELDS = { "Choice Themes", "Major Themes", "Minor Themes", }


def main():
    targets = []
    topictype = set()
    themepurge = set()
    themerename = {}
    parentage = {}
    definedthemes = set()
    referencedthemes = set()

    for arg in sys.argv[2:]:
        targets.extend(glob.glob(arg))

    for target in targets:
        if target.endswith("st.txt"):
            topictype.add('st')
        if target.endswith("th.txt"):
            topictype.add('th')
        if target.endswith(".xlsx"):
            lib.log.info("READING: %s", target)
            for name, sheet in lib.xls.xls_sheet_to_memory(target).items():
                headers = sheet[0]
                try:
                    themeidx = headers.index('Theme')
                    ppidx = headers.index('Proposed Parents')
                    tidx = headers.index('Thoughts')
                    aidx = headers.index('Action')
                except ValueError:
                    continue
                for row in sheet[1:]:
                    theme = row[themeidx].strip()
                    parents = row[ppidx].strip()
                    thoughts = row[tidx].strip()
                    action = row[aidx].strip()
                    if theme:
                        if action == 'delete':
                            themepurge.add(theme)
                        if thoughts.startswith(">"):
                            themerename[theme] = thoughts[1:].strip()
                        if parents:
                            parentage[theme] = parents

    for theme in themepurge:
        lib.log.info("DELETE: %s", theme)
    for theme, nname in themerename.items():
        lib.log.info("RENAME: %s => %s", theme, nname)
    for theme, parents in parentage.items():
        if not parents:
            if theme not in themepurge and theme not in themerename:
                lib.log.info("MISSING PARENTS: %s", theme)

    try:
        os.mkdir("_stage")
    except OSError:
        pass

    for target in targets:
        for thistopic in topictype:
            suffix = '.{}.txt'.format(thistopic)
            if target.endswith(suffix):
                break
        else:
            continue

        topicorder = []
        foundfields = set()
        topics = defaultdict(list)
        lib.log.info("READING: %s", target)
        stuff, notices = lib.dataparse.parse(target, default_parser='NOOP')
        for notice in notices:
            lib.log.error("%s: %s", target, notice)
        for topic, field, lines in stuff:
            if topic not in topics:
                topicorder.append(topic)
            foundfields.add(field)
            value = '\n'.join(lines)
            topics[topic].append([field, value])
        lines = []
        for topic in topicorder:
            if thistopic == 'th':
                topic = themerename.get(topic, topic)
                if topic in themepurge:
                    continue
                definedthemes.add(topic)
            lines.append(topic)
            lines.append("=" * len(topic))
            lines.append("")
            for field, value in topics[topic]:
                lines.append(":: " + field)
                if field in THEME_FIELDS:
                    newthemes = []
                    for kw, com, imp, cap in lib.dataparse.expload_field(value):
                        kw = themerename.get(kw, kw)
                        if not kw in themepurge:
                            newthemes.append((kw, com, imp, cap))
                    value = lib.dataparse.make_themes(newthemes)
                if thistopic == 'th' and field == "Parents":
                    value = parentage.get(topic, "") or value
                    referencedthemes.update([x.strip() for x in value.split(",") if x.strip()])
                if value.strip():
                    lines.append(value.strip("\n"))
                lines.append("")
            lines.append("")

        filename = os.path.basename(target)
        outfilename = os.path.join("_stage", filename)
        lib.log.info("WRITING: %s", outfilename)
        with codecs.open(outfilename, "w", "utf-8") as fh:
            for line in lines:
                fh.write(line + "\n")

    for theme in (referencedthemes - definedthemes):
        lib.log.info("UNDEFINED THEME: %s", theme)

