import lib.log
import lib.datastats
from random import random as rnd
import random
import urllib
import credentials
import lib.email
import os
import os.path
import datetime
import m4.tasks


DEBUG = False


def rchoice(ramp):
    """
    Args:
        ramp: list of (p, object) where p are cumulative probabilities  normalized
        so that the las p is always 1.0.
    Returns:
    An object picked uniformely at randomly from the ramp.
    """
    r = rnd()
    for p, obj in ramp:
        if r <= p:
            return obj
    if ramp:
        return ramp[-1][-1]  # should never happen


def build_theme_ramp():
    """
    Create [[pc, tobj], ...], where "pc" is a cumulative probability reflecting how
    used a theme is, and "tobj" is a corresponding theme object.

    Returns:
    [[pc, tobj], ...]
    """
    themes = lib.datastats.themes_with_usage()
    tramp = []
    ssum = 0
    for theme, tobj in themes.items():
        scount = len(tobj.stories)
        if scount > 2:
            ssum += scount
            tramp.append([ssum, tobj])
    for item in tramp:
        item[0] /= float(ssum)
    return tramp


def picktheme(tobjs, cutoffs=(2, 20), excluding=()):
    """
    Choose a theme object that is used in some, but not too many, stories.
    """
    for _ in range(100):
        tobj = random.choice(tobjs)
        if cutoffs[0] <= len(tobj.stories) < cutoffs[1] and tobj.name not in excluding:
            return tobj
    return tobj


def pickstory(stobjs, excluding=(), minorleap=False):
    """
    Choose a story, with high preference for those with stronger weight.
    """
    ww = {'choice': 75, 'major': 50, 'minor': 1}
    if minorleap:
        ww["minor"] += 10000
    ramp = []
    sumw = 0.0
    for stobj in stobjs:
        if stobj.name1 not in excluding:
            sumw += ww[stobj.weight]
            ramp.append([sumw, stobj])
    if not ramp:
        return pickstory(stobjs)
    for item in ramp:
        item[0] /= sumw
    return rchoice(ramp)


def extend_list(stlist, minorleap=False):
    """
    Given a list of [[storyobj, themeobj]] pairs, use the last theme to choose another
    story and theme that are somewhat similar. Add the new choice to the end of the list.

    Args:
        minorleap: If True, prefer stories that use the previous theme as minor.

    Returns:
    same list as input but with an added item
    """
    stories = lib.datastats.stories_with_themes()
    themes = lib.datastats.themes_with_usage()
    usedstories = {x[0].name for x in stlist if x[0]}
    usedthemes = {x[1].name for x in stlist if x[1]}
    tobj = stlist[-1][-1]
    stobj = pickstory(tobj.stories.values(), excluding=usedstories, minorleap=True)
    sobjs = stories[stobj.name1]
    tobjlist = [to for to in themes.values() if to.name in sobjs.themes]
    tobj2 = picktheme(tobjlist, excluding=usedthemes)
    stlist.append((sobjs, tobj2))
    return stlist


def makemail(stlist, cutoff=5):
    """
    Create an email explaining the list as returned from extend_list.

    Args:
        cutoff: The first "cutoff" themes should be used ad central, the rest as peripheral.
    """
    themelist1 = "\n".join("<LI>%s</LI>" % tobj.name for _, tobj in stlist[:cutoff])
    themelist2 = "\n".join("<LI>%s</LI>" % tobj.name for _, tobj in stlist[cutoff:])
    explainedlist = ""
    spatt = "https://themeontology.org/story.php?name="
    tpatt = "https://themeontology.org/theme.php?name="

    for sobj, tobj in stlist:
        if sobj:
            stobj = sobj.themes[tobj.name]
            url = spatt + urllib.quote(sobj.name)
            sl = """<a href="%s">%s""" % (url, sobj.name)
            st = sobj.title
            smot = stobj.motivation
        else:
            sl, st, smot = "", "", ""
        url = tpatt + urllib.quote(tobj.name)
        tl = """<a href="%s">%s""" % (url, tobj.name)
        tp = tobj.parents
        explainedlist += """\n<tr>%s</tr>""" % "".join("<td>%s</td>" % x for x in (tl, tp, st, sl, smot))

    html = """
        <style>%s</style>
        <DIV style="margin-bottom: 1em;">
            <H4><b>Your friendly M-4 Themeontolonic Assistant</b> has a new challenge for you.</H4>
            <P>Go to <A href="https://themeontology.org/">https://themeontology.org/</A> for more information.</P>
        </DIV>
        <H5>Invent a story that combines the following central themes:</H5>
        <OL>%s</OL>
        <H5>Optionally, include the peripheral themes:</H5>
        <OL start="%s">%s</OL>
        <H5>Relevant Prior Art:</H5>
        <TABLE class="motable">
        <th>Theme</th>
        <th>Parents</th>
        <th colspan=2>From Story</th>
        <th>Comment</th>
        %s
        </TABLE>
    """ % (lib.email.ST_BASE, themelist1, cutoff+1, themelist2, explainedlist)
    return html


def create_challenge():
    """
    Returns:
    boto3 like email definition of challenge.
    """
    themes = lib.datastats.themes_with_usage()
    tobj = picktheme(themes.values())
    stlist = [[None, tobj]]
    for _ in range(3):
        extend_list(stlist)
    for _ in range(2):
        extend_list(stlist, minorleap=True)
    for sobj, tobj in stlist:
        print("%50s: %s" % (sobj.name[:45] if sobj else "", tobj.name))
    return makemail(stlist, cutoff=3)


def main():
    with m4.tasks.ctx():
        td = datetime.date.today()
        if td.weekday() == 5 or DEBUG:  # only run on Saturdays
            lib.log.info("It Is Saturday! Creating Challenge...")
            tds = td.isoformat()
            basepath = os.path.join(credentials.PUBLIC_DIR, "m4", "challenge")
            path = os.path.join(basepath, tds + ".html")
            if not os.path.exists(path) or DEBUG:
                html = create_challenge()
                lib.email.publish(html,
                    mailsubject="M-4 Creative Challenge",
                    filepath=path,
                    slackmessage="Beep beep, I have a new challenge for you here:",
                )
            else:
                lib.log.info("Challenge for today already created.")
        else:
            lib.log.info("It is not Saturday :(")




















