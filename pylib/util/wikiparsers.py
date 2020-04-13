import urllib2
import re
from dateutil import parser
from bs4 import BeautifulSoup
import webobject
import json
import sys
import pdb
from collections import deque, defaultdict


REFSTRIPPER = re.compile(ur"\[\d+\]")


def get_date(datefield, regex, patt):
    """

    :param regex:
    :param patt:
    :return:
    """

    try:
        date1 = re.search("(\d{4}-\d{2}-\d{2})", datefield).group(0)
        return parser.parse(date1).strftime("%Y-%m-%d")
    except AttributeError:
        return None


def get_author(authorfield):
    """

    Args:
        authorfield:

    Returns:

    """
    acc = u""
    names = []
    for el in authorfield:
        if "<br" in unicode(el).lower():
            acc += u"\n"
        elif hasattr(el, "get_text"):
            acc += el.get_text()
        else:
            acc += unicode(el)
    for line in acc.split(u"\n"):
        if ":" in line:
            names.append(line.split("\n")[0].split(":")[1].strip())
        else:
            names.append(line.strip())
    return ", ".join(names)


def get_descriptions(descfield):
    """

    Args:
        descfield:

    Returns:

    """
    acc = u""
    descs = []
    for el in descfield:
        if "<hr" in unicode(el).lower():
            descs.append(acc)
            acc = u""
        elif hasattr(el, "get_text"):
            acc += el.get_text()
        else:
            acc += unicode(el)
    descs.append(acc) # even if empty
    return descs


def find_episodes_st1(url, season_offsset, prefix, tableclass = "wikitable", cols = (1, 3, 4, 6), isterse = False):
    """

    :param url:
    :param season_offsset:
    :param prefix:
    :param tableclass:
    :param cols:
    :param isterse:
        By default we expect every other row in the list to contain a description that go along with the preceding
        row's information. If the description row is not present, set this flag.
    :return:
    """
    data = urllib2.urlopen(url).read()
    soup = BeautifulSoup(data, "html.parser")
    resturl = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    sidcounter = defaultdict(int)

    for idx, table in enumerate(soup.find_all("table", class_ = tableclass)):
        sids = []
        description = None
        titlestack = deque()
        coloffsetstack = deque()

        for row in table.find_all("tr"):
            tdfields = row.find_all("td")

            # no rowspan cols may be in between the indexes given with the "cols" argument, or things will break
            coloffset = coloffsetstack.popleft() if coloffsetstack else 0
            for td in tdfields[:min(cols)]:
                rowspan = int(td.attrs.get('rowspan', 0))
                while len(coloffsetstack) < rowspan:
                    coloffsetstack.append(0)
                for ii in range(rowspan):
                    coloffsetstack[ii] += 1

            if len(tdfields) > max(cols) - coloffset:
                titlefield = tdfields[cols[0] - coloffset]
                directorfield = tdfields[cols[1] - coloffset]
                authorfield = tdfields[cols[2] - coloffset]
                datefield = tdfields[cols[3] - coloffset]

                title_link = titlefield.find("a")
                title = titlefield.get_text().strip(" \"")
                datetext = datefield.get_text().strip()
                date = None

                for regex in [
                    r"(\d{4}-\d{2}-\d{2})", #yyyy-mm-dd
                    r"(\w+ \d{1,2}, \d{4})", #MM dd, yyyy
                    r"(\d{1,2} \w+ \d{4})", #dd MM yyyy
                ]:
                    try:
                        date1 = re.search(regex, datetext).group(0)
                        date = parser.parse(date1).strftime("%Y-%m-%d")
                        break
                    except AttributeError:  # no regex match
                        pass

                if not coloffset:
                    epfield = row.find("td").get_text()
                author = "Story by: " + get_author(authorfield)
                director = "Directed by: " + directorfield.get_text()

                #sys.stderr.write(str(authorfield).decode("utf-8").encode("ascii", "ignore") + "\n")
                #f = authorfield
                #pdb.set_trace()

                for match in re.findall("(\d+)([a-z]*)", epfield):
                    nepid, sepid = int(match[0]), match[1]
                    sid = prefix + "%sx%02d%s" % (idx + season_offsset, nepid, sepid)
                    sids.append(sid)

                if isterse and title_link:
                    suffix = title_link.get("href").split("/")[-1].strip()
                    descurl = resturl + suffix
                    jsondata = urllib2.urlopen(descurl).read()
                    info = json.loads(jsondata)
                    description = info['extract']

                titlestack.append((sid, title, director, author, date))
                print("ADD", titlestack[-1])

            else:
                descriptionfield = row.find("td", class_ = "description")
                if descriptionfield:
                    description = descriptionfield.get_text().strip()

            if description and sids:
                if descriptionfield:
                    desclist = get_descriptions(descriptionfield)
                else:
                    desclist = [description]
                numstories = min(len(desclist), len(titlestack))
                for description in desclist:
                    if not titlestack:
                        break
                    print("POP", titlestack[0])
                    sid, title, director, author, date = titlestack.popleft()
                    sidcounter[sid] += 1
                    if numstories > 1:
                        sid += chr(ord("a") + sidcounter[sid] - 1)
                    description = unicode(description).strip()
                    description = description + "\n\n" + director.strip(".") + ". " + author.strip(".") + ".\n"
                    description = REFSTRIPPER.sub(u"", description)

                    yield webobject.Story(
                        name = sid,
                        title = title,
                        description = description,
                        date = date,
                    )

                sids = []
                description = ''

