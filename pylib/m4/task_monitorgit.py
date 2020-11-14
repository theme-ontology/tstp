from __future__ import print_function
import lib.log
import sys
import lib.commits
import db
import subprocess
import re
from datetime import datetime, timedelta
import lib.email
import m4.tasks


DEBUG = False

NAUGHTY = ['2g1c', '2 girls 1 cup', 'anal', 'anus', 'arse', 'ass', 'asshole', 'arsehole', 'asswhole', 'assmunch',
           'auto erotic', 'autoerotic', 'ballsack', 'bastard', 'beastial', 'bellend', 'bitch', 'bitches', 'bitchin',
           'bitching', 'bimbo', 'bimbos', 'blow job', 'blowjob', 'blowjobs', 'blue waffle', 'boob', 'boobs', 'booobs',
           'boooobs', 'booooobs', 'booooooobs', 'brown shower', 'brown showers', 'boner', 'buceta', 'bukake',
           'bukkake', 'bullshit', 'bull shit', 'butthole', 'carpet muncher', 'cawk', 'chink', 'cipa', 'clit', 'clits',
           'cnut', 'cock', 'cocks', 'cockface', 'cockhead', 'cockmunch', 'cockmuncher', 'cocksuck', 'cocksucked',
           'cocksucking', 'cocksucks', 'cocksucker', 'cokmuncher', 'coon', 'cum', 'cummer', 'cumming', 'cuming',
           'cums', 'cumshot', 'cunilingus', 'cunillingus', 'cunnilingus', 'cunt', 'cuntlicker', 'cuntlicking', 'cunts',
           'dickhead', 'dildo', 'dildos', 'dink', 'dinks', 'deepthroat', 'deep throat', 'dog style', 'doggie style',
           'doggiestyle', 'doggy style', 'doggystyle', 'donkeyribber', 'doosh', 'douche', 'duche', 'dyke', 'ejakulate', 
           'fag', 'faggot', 'fagging', 'faggit', 'faggitt', 'faggs', 'fagot', 'fagots', 'fags', 'fatass', 'footjob',
           'foot job', 'fuck', 'fucks', 'fucker', 'fuckers', 'fucked', 'fuckhead', 'fuckheads', 'fuckin', 'fucking',
           'fcuk', 'fcuker', 'fcuking', 'felching', 'fellate', 'fellatio', 'fingerfuck', 'fingerfucked',
           'fingerfucker', 'fingerfuckers', 'fingerfucking', 'fingerfucks', 'fistfuck', 'fistfucked', 'fistfucker',
           'fistfuckers', 'fistfucking', 'fistfuckings', 'fistfucks', 'fook', 'fooker', 'fucka', 'fuk', 'fuks',
           'fuker', 'fukker', 'fukkin', 'fukking', 'futanari', 'futanary', 'gokkun', 'gaylord', 'gaysex', 'goatse',
           'handjob', 'hand job', 'hentai', 'hooker', 'hoer', 'homo', 'jackoff', 'jack off', 'jerkoff', 'jerk off',
           'jizz', 'kinbaku', 'labia', 'mofo', 'mothafuck', 'motherfuck', 'motherfucker', 'mothafucka', 'mothafuckas',
           'mothafuckaz', 'mothafucked', 'mothafucker', 'mothafuckers', 'mothafuckin', 'mothafucking', 'mothafuckings',
           'mothafucks', 'mother fucker', 'motherfucked', 'motherfucker', 'motherfuckers', 'motherfuckin',
           'motherfucking', 'motherfuckings', 'motherfuckka', 'motherfucks', 'milf', 'muff', 'nigga', 'nigger', 'nigg',
           'nob jokey', 'nobhead', 'nobjocky', 'nobjokey', 'numbnuts', 'nutsack', 'pron', 'pussy', 'pussies',
           'retard', 'schlong', 'shemale', 'she male', 'shibari', 'shibary', 'shit', 'shitdick', 'shitfuck',
           'shitfull', 'shithead', 'shiting', 'shitings', 'shits', 'shitted', 'shitters', 'shitting', 'shittings',
           'shitty', 'shota', 'skank', 'slut', 'sluts', 'smegma', 'spunk', 'tit', 'tits', 'titties', 'titty',
           'titfuck', 'tittiefucker', 'titties', 'tittyfuck', 'tittywank', 'titwank', 'throating', 'twat', 'twathead',
           'twatty', 'twunt', 'wank', 'wanker', 'wanky', 'whore', 'whoar', 'xxx', 'xx', 'yaoi', 'yury']
FOWL = [
    "Crow", "Peacock", "Dove", "Sparrow", "Goose", "Ostrich", "Pigeon", "Tit", "Turkey", "Hawk", "Bald eagle", "Raven",
    "Parrot", "Flamingo", "Seagull", "Swallow", "Blackbird", "Penguin", "Robin", "Swan", "Owl" "Stork", "Woodpecker",
]
NAUGHTYSTEMS = {}


def profanities(text):
    """
    Args:
        text:  unified diff
    Returns:
        A list of those lines that begin with "+" and seem to contain foul language.
    """
    global NAUGHTYSTEMS
    suspicious = []
    try:
        from nltk.stem import PorterStemmer
        from nltk.tokenize import word_tokenize
    except ImportError:
        lib.log.error("Failed to import NLTK, foul language detection disabled")
        return suspicious
    ps = PorterStemmer()
    if not NAUGHTYSTEMS:
        NAUGHTYSTEMS = {ps.stem(w.lower()): (w, "naughty") for w in NAUGHTY}
        NAUGHTYSTEMS.update({ps.stem(w.lower()): (w, "fowl") for w in FOWL})
    for line in text.split("\n"):
        wline = line.strip().lower()
        if wline.startswith("+"):
            wline = re.sub("[^\w']", " ", wline)
            try:
                stems = set(ps.stem(w) for w in word_tokenize(wline))
            except LookupError:
                lib.log.error("Failed to tokenize with NLTK, foul language detection disabled")
                return suspicious
            matches = [(k,) + NAUGHTYSTEMS[k] for k in stems if k in NAUGHTYSTEMS]
            if matches:
                suspicious.append((line, matches))
    return suspicious


def makemail(entries, txtdiff):
    """
    Create an email definition suiting Amazon SES boto3 API.
    Args:
        entries:
        txtdiff: A piece of unified diff.

    Returns: Dictionary corresponding to message part of SES boto3 API.
    """
    from pygments import highlight
    from pygments.lexers import DiffLexer
    from pygments.formatters import HtmlFormatter

    loglines = []
    naughtyblock = ""
    pieces = []
    filediffs = ""
    hfmt = HtmlFormatter(style="rainbow_dash", noclasses=True)
    subjectline = "M-4 Yellow Alert!"

    for entry in entries:
        rev, ctime, author, committype, msg = entry[:5]
        if committype != "merge":
            ctime = ctime.strftime('%Y-%m-%d %H:%M:%S')
            arev = """<A href="https://github.com/theme-ontology/theming/commit/%s">%s..</A>""" % (rev, rev[:6])
            loglines.append("""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (arev, ctime, author, msg))

    for line in txtdiff.split("\n"):
        match = re.match("^diff --git a/(.+?) b/(.+?)$", line)
        if match:
            pieces.append([])
        if pieces:
            pieces[-1].append(line.strip())
    for block in pieces:
        txt = '\n'.join(block)
        naughtylines = profanities(txt)
        filediffs += """\n%s""" % highlight(txt, DiffLexer(), hfmt)

    if naughtylines:
        if len(naughtylines) > 1:
            subjectline = "M-4 Double Red Alert!"
        else:
            subjectline = "M-4 Red Alert!"
        badlines = "\n".join(x[0] for x in naughtylines)
        badtypes, badexplain = [], []
        for _line, matches in naughtylines:
            badtypes.extend(x[2].capitalize() for x in matches)
            badexplain.extend((x[0], x[1]) for x in matches)
        badtypes = " and ".join(sorted(set(badtypes), reverse=True))
        badexplain = ', '.join('"%s" => "%s"' % x for x in sorted(set(badexplain)))
        naughtyblock = """
    <DIV style="background:#ff8888; padding: .1em .5em; margin: 1em 0em;">
        <H4>Potentially %s Language Detected in the Vicinity of M-4:</H4>
        <PRE>%s</PRE>
        <i style="font-size: xx-small;">%s</i>
    </DIV>
""" % (badtypes, badlines, badexplain)

    style = lib.email.ST_BASE + lib.email.ST_REAL_RAINBOW_DASH
    htmldiff = """
        <style>
        table.rainbow_dashtable {
        }
        %s
        </style>
        <DIV style="margin-bottom: 1em;">
            <H4><b>Your friendly M-4 Themeontolonic Assistant</b> detected changes in GIT.</H4>
            <P>Go to <A href="https://themeontology.org/">https://themeontology.org/</A> for more information.</P>
        </DIV>
        %s
        <TABLE class="motable">
        <tr>
            <th>rev</th>
            <th>utc</th>
            <th>author</th>
            <th>comment</th>
        </tr>
        %s
        </TABLE>
        %s
""" % (style, naughtyblock, "\n".join(loglines), filediffs)

    return {
        "Body": {
            "Html": {
                "Charset": "UTF-8",
                "Data": htmldiff,
            },
        },
        "Subject": {
            "Charset": "UTF-8",
            "Data": subjectline,
        },
    }


def react_to_commit():
    """
    M-4 will do a variety of things when there is a new commit.
    """
    if "--debug" in sys.argv:
        global DEBUG
        DEBUG = True
    if DEBUG:
        args = [x for x in sys.argv if x.startswith("--dt")]
        hours = int(args[-1][4:]) if args else 24
        ts = (datetime.utcnow() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        db.do("""DELETE FROM commits_log WHERE time > '%s'""" % ts)
    commitslog = list(db.do("""SELECT id, time FROM commits_log ORDER BY time DESC LIMIT 1"""))
    if commitslog:
        fromid, fromtime = commitslog[0]
        sfromtime = fromtime.strftime('%Y-%m-%d %H:%M:%S')
        lib.log.debug("last previously known commit is %s at %s", fromid, sfromtime)
        lib.commits.dbstore_commit_data(fromdate=fromtime, recreate=False, quieter=True)
    else:
        lib.log.debug("no previous commits logged, running from scratch...")
        lib.commits.dbstore_commit_data(fromdate=None, recreate=True, quieter=False)

    entries = list(db.do("""
        SELECT id, time, author, committype, message FROM commits_log
        WHERE time > '%s' ORDER BY time ASC""" % sfromtime
    ))
    if not entries:
        lib.log.debug("NO NEW CHANGES! Aborting.")
    else:
        toid, totime = entries[-1][:2]
        stotime = totime.strftime('%Y-%m-%d %H:%M:%S')
        lib.log.debug("last newly discovered commit is %s at %s", toid, stotime)
        diffcmd = 'git diff %s..%s' % (fromid, toid)
        txtdiff = subprocess.check_output(diffcmd.split()).decode("utf-8")
        if DEBUG:
            txtdiff += """+ and some profane shit\n"""
            txtdiff += """+ you Dick\n"""
            txtdiff += """+ look, a Tit\n"""
            pass
        maildef = makemail(entries, txtdiff)
        lib.email.sendmail(maildef)


def main():
    with m4.tasks.ctx():
        react_to_commit()




















