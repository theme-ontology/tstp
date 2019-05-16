import urllib2
import re
from dateutil import parser
from bs4 import BeautifulSoup
import webobject
import json


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

    for idx, table in enumerate(soup.find_all("table", class_ = tableclass)):
        sids = []
        description = None

        for row in table.find_all("tr"):
            tdfields = row.find_all("td")
            if len(tdfields) > max(cols):
                titlefield = tdfields[cols[0]]
                directorfield = tdfields[cols[1]]
                authorfield = tdfields[cols[2]]
                datefield = tdfields[cols[3]]

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

                epfield = row.find("td").get_text()
                author = authorfield.get_text()
                director = "Directed by: " + directorfield.get_text()

                if ":" in author:
                    author = "Story by:" + author.split("\n")[0].split(":")[1]
                else:
                    author = "Story by: " + author

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

            else:
                try:
                    description = row.find("td", class_ = "description")
                    description = description.get_text().strip()
                except AttributeError:
                    pass # found no description

            if description and sids:
                description = description + "\n\n" + director.strip(".") + ". " + author.strip(".") + ".\n"

                for sid in sids:
                    yield webobject.Story(
                        name = sid,
                        title = title,
                        description = description,
                        date = date,
                    )

                sids = []
                description = ''
