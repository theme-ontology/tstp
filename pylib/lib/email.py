import lib.log
import credentials
import lib.files
import requests
import json


ST_BASE = """
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

ST_REAL_RAINBOW_DASH = """
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
"""


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


def publish(html, mailsubject=None, slackmessage=None, filepath=None):
    """
    Publish html data in a variety of ways.
    Args:
        html: Html content to publish.
        mailsubject: If emailing, subject of email.
        slackmessage: If posting to slack, mrkdwn text message to include.
        filepath: If saving as a file, path to file. If path is in public dir, a url
            will be in included in the slack message.
    Returns: None
    """
    url = None
    if lib.files.preparefile(filepath):
        with open(filepath, "w+") as fh:
            fh.write(html)
    if filepath:
        url = lib.files.path2url(filepath)
    if mailsubject:
        sendmail({
            "Body": {
                "Html": {
                    "Charset": "UTF-8",
                    "Data": html,
                },
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": mailsubject,
            },
        })
    if slackmessage:
        data = {
            "blocks": [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": slackmessage,
                },
            }],
        }
        if url:
            data["blocks"][-1]["text"]["text"] += " " + url
        lib.log.info("Posting to slack...")
        response = requests.post(
            credentials.SLACK_WEBHOOK_URL,
            headers={'Content-type': 'application/json'},
            data=json.dumps(data),
        )
        code = response.status_code
        if code != 200:
            lib.log.error("Something went wrong, response code: %s", code)



























