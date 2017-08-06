import urllib2
import re
import datetime
from dateutil import parser

from bs4 import BeautifulSoup

import webdb
import webobject


def find_episodes_st1(url, season_offsset, prefix, tableclass = "wikitable", cols = (1, 3, 4, 6)):
    data = urllib2.urlopen(url).read()
    soup = BeautifulSoup(data, "html.parser")

    for idx, table in enumerate(soup.find_all("table", class_ = tableclass)):
        sids = []
        
        for row in table.find_all("tr"):
            tdfields = row.find_all("td")

            if len(tdfields) > 6:
                titlefield = tdfields[cols[0]]
                directorfield = tdfields[cols[1]]
                authorfield = tdfields[cols[2]]
                datefield = tdfields[cols[3]]

                title = titlefield.get_text().strip(" \"")
                date1 = re.search("(\d{4}-\d{2}-\d{2})", datefield.get_text().strip()).group(0)
                date = parser.parse(date1).strftime("%Y-%m-%d")
                assert date == date1
                epfield = row.find("td").get_text()
                author = authorfield.get_text()
                director = "Directed by: " + directorfield.get_text()

                if ":" in author:
                    author = "Story by:" + author.split("\n")[0].split(":")[1]
                else:
                    author = "Story by: " + author

                for match in re.findall("\d+", epfield):
                    sid = prefix + "%sx%02d" % (idx + season_offsset, int(match))
                    sids.append(sid)

            else:
                description = row.find("td", class_ = "description")

                if description and sids:
                    description = description.get_text().strip()
                    description = description + "\n\n" + director.strip(".") + ". " + author.strip(".") + ".\n"

                    for sid in sids:
                        yield webobject.Story(
                            name = sid,
                            title = title,
                            description = description,
                            date = date,
                        )
                    sids = []

