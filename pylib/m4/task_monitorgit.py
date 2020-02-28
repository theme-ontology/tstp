import lib.log
import sys
import lib.commits
import db
import subprocess
import re
import credentials
from collections import OrderedDict


DEBUG = False
REAL_RAINBOW_DASH = """
.highlight .hll { background-color: #ffffcc }
.highlight .c { color: #0080ff; font-style: italic } /* Comment */
.highlight .err { color: #ffffff; background-color: #cc0000 } /* Error */
.highlight .k { color: #2c5dcd; font-weight: bold } /* Keyword */
.highlight .o { color: #2c5dcd } /* Operator */
.highlight .ch { color: #0080ff; font-style: italic } /* Comment.Hashbang */
.highlight .cm { color: #0080ff; font-style: italic } /* Comment.Multiline */
.highlight .cp { color: #0080ff } /* Comment.Preproc */
.highlight .cpf { color: #0080ff; font-style: italic } /* Comment.PreprocFile */
.highlight .c1 { color: #0080ff; font-style: italic } /* Comment.Single */
.highlight .cs { color: #0080ff; font-weight: bold; font-style: italic } /* Comment.Special */
.highlight .gd { background-color: #ffcccc; border: 1px solid #c5060b } /* Generic.Deleted */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gr { color: #ff0000 } /* Generic.Error */
.highlight .gh { color: #2c5dcd; font-weight: bold } /* Generic.Heading */
.highlight .gi { background-color: #ccffcc; border: 1px solid #00cc00 } /* Generic.Inserted */
.highlight .go { color: #aaaaaa } /* Generic.Output */
.highlight .gp { color: #2c5dcd; font-weight: bold } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #2c5dcd; font-weight: bold } /* Generic.Subheading */
.highlight .gt { color: #c5060b } /* Generic.Traceback */
.highlight .kc { color: #2c5dcd; font-weight: bold } /* Keyword.Constant */
.highlight .kd { color: #2c5dcd; font-weight: bold } /* Keyword.Declaration */
.highlight .kn { color: #2c5dcd; font-weight: bold } /* Keyword.Namespace */
.highlight .kp { color: #2c5dcd } /* Keyword.Pseudo */
.highlight .kr { color: #2c5dcd; font-weight: bold } /* Keyword.Reserved */
.highlight .kt { color: #5918bb; font-weight: bold } /* Keyword.Type */
.highlight .m { color: #5918bb; font-weight: bold } /* Literal.Number */
.highlight .s { color: #00cc66 } /* Literal.String */
.highlight .na { color: #2c5dcd; font-style: italic } /* Name.Attribute */
.highlight .nb { color: #5918bb; font-weight: bold } /* Name.Builtin */
.highlight .nc { text-decoration: underline } /* Name.Class */
.highlight .no { color: #318495 } /* Name.Constant */
.highlight .nd { color: #ff8000; font-weight: bold } /* Name.Decorator */
.highlight .ni { color: #5918bb; font-weight: bold } /* Name.Entity */
.highlight .ne { color: #5918bb; font-weight: bold } /* Name.Exception */
.highlight .nf { color: #ff8000; font-weight: bold } /* Name.Function */
.highlight .nt { color: #2c5dcd; font-weight: bold } /* Name.Tag */
.highlight .ow { color: #2c5dcd; font-weight: bold } /* Operator.Word */
.highlight .w { color: #cbcbcb } /* Text.Whitespace */
.highlight .mb { color: #5918bb; font-weight: bold } /* Literal.Number.Bin */
.highlight .mf { color: #5918bb; font-weight: bold } /* Literal.Number.Float */
.highlight .mh { color: #5918bb; font-weight: bold } /* Literal.Number.Hex */
.highlight .mi { color: #5918bb; font-weight: bold } /* Literal.Number.Integer */
.highlight .mo { color: #5918bb; font-weight: bold } /* Literal.Number.Oct */
.highlight .sa { color: #00cc66 } /* Literal.String.Affix */
.highlight .sb { color: #00cc66 } /* Literal.String.Backtick */
.highlight .sc { color: #00cc66 } /* Literal.String.Char */
.highlight .dl { color: #00cc66 } /* Literal.String.Delimiter */
.highlight .sd { color: #00cc66; font-style: italic } /* Literal.String.Doc */
.highlight .s2 { color: #00cc66 } /* Literal.String.Double */
.highlight .se { color: #c5060b; font-weight: bold } /* Literal.String.Escape */
.highlight .sh { color: #00cc66 } /* Literal.String.Heredoc */
.highlight .si { color: #00cc66 } /* Literal.String.Interpol */
.highlight .sx { color: #318495 } /* Literal.String.Other */
.highlight .sr { color: #00cc66 } /* Literal.String.Regex */
.highlight .s1 { color: #00cc66 } /* Literal.String.Single */
.highlight .ss { color: #c5060b; font-weight: bold } /* Literal.String.Symbol */
.highlight .bp { color: #5918bb; font-weight: bold } /* Name.Builtin.Pseudo */
.highlight .fm { color: #ff8000; font-weight: bold } /* Name.Function.Magic */
.highlight .il { color: #5918bb; font-weight: bold } /* Literal.Number.Integer.Long */
div.highlight {
    margin: 1em 0em;
    padding: 0em .5em;
    background: #efedeb;
    color: #4d4d4d;
    border: 1px solid #c8c4c0;
    overflow-x: auto;
}
table.motable {
    font-family: "Courier", Monaco, monospace;
    font-size: .75em;
    border: 1px solid #c8c4c0;
    background-color: #EBEBEB;
    text-align: left;
    border-collapse: collapse;
}
table.motable td, table.motable th {
    border: 1px solid #FFFFFF;
    padding: 5px 10px;
}
table.motable tbody td {
}
table.motable tr:nth-child(even) {
    background: #DDDDDD;
}
table.motable thead {
    background: #A4A4A4;
}
table.motable thead th {
    font-weight: bold;
    text-align: left;
}
table.motable tfoot td {
}
table.motable tfoot .links {
    text-align: right;
}
table.motable tfoot .links a{
    display: inline-block;
    background: #FFFFFF;
    color: #398AA4;
    padding: 2px 8px;
    border-radius: 5px;
}
H4, P {
    font-family: sans-serif;
    margin: .2em 0em;
}
pre {
    font-size: normal;
}
"""

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


def sendmail(maildef):
    """
    Send email using Amazon SES via boto3.
    Args:
        maildef: SES boto3 API.
    """
    import boto3
    sendermail = "M-4 Assistant <noreply@themeontology.org>"
    client = boto3.client('ses')
    for targetmail in credentials.EMAIL_ADMIN:
        try:
            response = client.send_email(
                Destination={"ToAddresses": [targetmail]},
                Message=maildef,
                Source=sendermail,
            )
            lib.log.debug(response)
        except client.exceptions.MessageRejected:
            lib.log.error("Failed to send email to %s", targetmail)


def profanities(text):
    """
    Args:
        text:  unified diff
    Returns:
        A list of those lines that begin with "+" and seem to contain foul language.
    """
    suspicious = []
    for line in text.split("\n"):
        line = line.strip().lower()
        if line.startswith("+"):
            if any(" "+x in line for x in NAUGHTY):
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
""" % (REAL_RAINBOW_DASH, naughtyblock, "\n".join(loglines), filediffs)

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


def main():
    lib.log.info("task starting")
    lib.log.LOGTARGET.flush()

    #db.do("""DELETE FROM commits_log WHERE time > '2020-02-28 00:00:00'""")

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
        #txtdiff += """+ and some profane shit\n"""
        maildef = makemail(entries, txtdiff)
        sendmail(maildef)

    sys.stdout.flush()
    sys.stderr.flush()
    lib.log.LOGTARGET.flush()
    lib.log.info("task finished")




