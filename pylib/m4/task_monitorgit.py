import lib.log
import sys
import lib.commits
import db
import subprocess
import re
from datetime import datetime, timedelta
import lib.email
import m4.tasks
import tests


DEBUG = False

NAUGHTY = ['2g1c', '2 girls 1 cup', 'anal', 'anus', 'arse', 'ass', 'asshole', 'arsehole', 'asswhole', 'assmunch',
           'auto erotic', 'autoerotic', 'ballsack', 'bastard', 'beastial', 'bellend', 'bdsm', 'bestiality', 'bitch',
           'bitches', 'bitchin', 'bitching', 'bimbo', 'bimbos', 'blow job', 'blowjob', 'blowjobs', 'blue waffle',
           'boob', 'boobs', 'booobs', 'boooobs', 'booooobs', 'booooooobs', 'breasts', 'booty call', 'brown shower',
           'brown showers', 'boner', 'bondage', 'buceta', 'bukake', 'bukkake', 'bullshit', 'bull shit', 'busty',
           'butthole', 'carpet muncher', 'cawk', 'chink', 'cipa', 'clit', 'clits', 'clitoris', 'cnut', 'cock', 'cocks',
           'cockface', 'cockhead', 'cockmunch', 'cockmuncher', 'cocksuck', 'cocksucked', 'cocksucking', 'cocksucks',
           'cocksucker', 'cokmuncher', 'coon', 'cow girl', 'cow girls', 'cowgirl', 'cowgirls', 'crap', 'crotch',
           'cum', 'cummer', 'cumming', 'cuming', 'cums', 'cumshot', 'cunilingus', 'cunillingus', 'cunnilingus',
           'cunt', 'cuntlicker', 'cuntlicking', 'cunts', 'damn', 'dick', 'dickhead', 'dildo', 'dildos', 'dink',
           'dinks', 'deepthroat', 'deep throat', 'dog style', 'doggie style', 'doggiestyle', 'doggy style',
           'doggystyle', 'donkeyribber', 'doosh', 'douche', 'duche', 'dyke', 'ejaculate', 'ejaculated', 'ejaculates',
           'ejaculating', 'ejaculatings', 'ejaculation', 'ejakulate', 'erotic', 'erotism', 'fag', 'faggot',
           'fagging', 'faggit', 'faggitt', 'faggs', 'fagot', 'fagots', 'fags', 'fatass', 'femdom', 'fingering',
           'footjob', 'foot job', 'fuck', 'fucks', 'fucker', 'fuckers', 'fucked', 'fuckhead', 'fuckheads', 'fuckin',
           'fucking', 'fcuk', 'fcuker', 'fcuking', 'felching', 'fellate', 'fellatio', 'fingerfuck', 'fingerfucked',
           'fingerfucker', 'fingerfuckers', 'fingerfucking', 'fingerfucks', 'fistfuck', 'fistfucked', 'fistfucker',
           'fistfuckers', 'fistfucking', 'fistfuckings', 'fistfucks', 'flange', 'fook', 'fooker', 'fucka', 'fuk',
           'fuks', 'fuker', 'fukker', 'fukkin', 'fukking', 'futanari', 'futanary', 'gangbang', 'gangbanged',
           'gang bang', 'gokkun', 'golden shower', 'goldenshower', 'gay', 'gaylord', 'gaysex', 'goatse', 'handjob',
           'hand job', 'hentai', 'hooker', 'hoer', 'homo', 'horny', 'incest', 'jackoff', 'jack off', 'jerkoff',
           'jerk off', 'jizz', 'knob', 'kinbaku', 'labia', 'lesbian', 'masturbate', 'masochist', 'mofo', 'mothafuck',
           'motherfuck', 'motherfucker', 'mothafucka', 'mothafuckas', 'mothafuckaz', 'mothafucked', 'mothafucker',
           'mothafuckers', 'mothafuckin', 'mothafucking', 'mothafuckings', 'mothafucks', 'mother fucker',
           'motherfucked', 'motherfucker', 'motherfuckers', 'motherfuckin', 'motherfucking', 'motherfuckings',
           'motherfuckka', 'motherfucks', 'milf', 'muff', 'nigga', 'nigger', 'nigg', 'nipple', 'nipples', 'nob',
           'nob jokey', 'nobhead', 'nobjocky', 'nobjokey', 'numbnuts', 'nutsack', 'nude', 'nudes', 'orgy', 'orgasm',
           'orgasms', 'panty', 'panties', 'penis', 'playboy', 'porn', 'porno', 'pornography', 'pron', 'pussy',
           'pussies', 'rape', 'raping', 'rapist', 'rectum', 'retard', 'rimming', 'sadist', 'sadism', 'schlong',
           'scrotum', 'sex', 'semen', 'shemale', 'she male', 'shibari', 'shibary', 'shit', 'shitdick', 'shitfuck',
           'shitfull', 'shithead', 'shiting', 'shitings', 'shits', 'shitted', 'shitters', 'shitting', 'shittings',
           'shitty', 'shota', 'skank', 'slut', 'sluts', 'smut', 'smegma', 'spunk', 'strip club', 'stripclub', 'tit',
           'tits', 'titties', 'titty', 'titfuck', 'tittiefucker', 'titties', 'tittyfuck', 'tittywank', 'titwank',
           'threesome', 'three some', 'throating', 'twat', 'twathead', 'twatty', 'twunt', 'viagra', 'vagina',
           'vulva', 'wank', 'wanker', 'wanky', 'whore', 'whoar', 'xxx', 'xx', 'yaoi', 'yury']
NAUGHTYSTEMS = []


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
        NAUGHTYSTEMS = set(ps.stem(w) for w in NAUGHTY)
    for line in text.split("\n"):
        wline = line.strip().lower()
        if wline.startswith("+"):
            wline = re.sub("[^\w']", " ", wline)
            try:
                stems = set(ps.stem(w) for w in word_tokenize(wline))
            except LookupError:
                lib.log.error("Failed to tokenize with NLTK, foul language detection disabled")
                return suspicious
            if stems.intersection(NAUGHTYSTEMS):
                suspicious.append(line)
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
        rev, ctime, author, msg = entry[:4]
        ctime = ctime.strftime('%Y-%m-%d %H:%M:%S')
        arev = """<A href="https://github.com/theme-ontology/theming/commit/%s">%s</A>""" % (rev, rev)
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
        naughtyblock = """
    <DIV style="background:#ff8888; padding: .1em .5em; margin: 1em 0em;">
        <H4>Potentially Foul Language Detected in the Vicinity of M-4:</H4>
        <PRE>%s</PRE></DIV>
""" % "\n".join(naughtylines)

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
    if DEBUG:
        ts = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        db.do("""DELETE FROM commits_log WHERE time > '%s'""" % ts)
    fromid, fromtime = list(db.do("""SELECT id, time FROM commits_log ORDER BY time DESC LIMIT 1"""))[0]
    sfromtime = fromtime.strftime('%Y-%m-%d %H:%M:%S')
    lib.log.debug("last previously known commit is %s at %s", fromid, sfromtime)
    lib.commits.dbstore_commit_data(fromdate=fromtime, recreate=False, quieter=True)
    entries = list(db.do("""
        SELECT id, time, author, message FROM commits_log
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
            pass
        maildef = makemail(entries, txtdiff)
        lib.email.sendmail(maildef)


def main():
    with m4.tasks.ctx():
        react_to_commit()




















