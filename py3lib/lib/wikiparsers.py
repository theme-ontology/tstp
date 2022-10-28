import urllib.request
import re
from dateutil import parser
from bs4 import BeautifulSoup
import webobject
import json
import sys
import pdb
from collections import deque, defaultdict
from pprint import pprint as pp

REFSTRIPPER = re.compile(r"\[\d+\]")


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
    acc = ""
    names = []
    for el in authorfield:
        if "<br" in str(el).lower():
            acc += "\n"
        elif hasattr(el, "get_text"):
            acc += el.get_text()
        else:
            acc += el
    for line in acc.split("\n"):
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
        if "<hr" in str(el).lower():
            descs.append(acc)
            acc = u""
        elif hasattr(el, "get_text"):
            acc += el.get_text()
        else:
            acc += el
    descs.append(acc)  # even if empty
    return descs


def get_date(datetext):
    """

    Args:
        datefield:

    Returns:

    """
    date = None
    for regex in [
        r"(\d{4}-\d{2}-\d{2})",  # yyyy-mm-dd
        r"(\w+ \d{1,2}, \d{4})",  # MM dd, yyyy
        r"(\d{1,2} \w+ \d{4})",  # dd MM yyyy
        r"(\d{4})",  # yyyy
    ]:
        try:
            datematch = re.search(regex, datetext).group(0)
            date = parser.parse(datematch).strftime("%Y-%m-%d")
            if len(datematch) <= 4:
                date = datematch
            break
        except AttributeError:  # no regex match
            pass

    return date


def fetch_info(wikipagename):
    resturl = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    descurl = resturl + wikipagename
    with urllib.request.urlopen(descurl) as response:
        jsondata = response.read()
    info = json.loads(jsondata)
    return info


def fetch_links_info(url, filter="/wiki/", startafter="/wiki/Help:Maintenance", stopat="/wiki/Help:Category"):
    """
    Open url, extract qualifying wikipedia links and then read json page summary
    for those links using fetch_info.
    Args:
        url:
    Returns: yield (title, page-name, json info) tuples.
    """
    started = False
    with urllib.request.urlopen(url) as response:
        data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all("a"):
        url2 = link.get("href")
        if url2:
            if not started:
                if re.match(startafter, url2):
                    started = True
                continue
            if re.match(stopat, url2):
                break
            if re.match(filter, url2):
                print(url2)
                title = link.get_text()
                pagename = url2.rsplit("/")[-1]
                yield title, pagename, fetch_info(pagename)


def fetch_table_list(url, tableclass="wikitable", cols=(0, 1, 5, 2)):
    """

    Args:
        url:

    Returns:

    """
    with urllib.request.urlopen(url) as response:
        data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    sidcounter = defaultdict(int)
    descriptionfield = None

    for idx, table in enumerate(soup.find_all("table", class_=tableclass)):
        for row in table.find_all("tr"):
            tdfields = row.find_all("td")

            if len(tdfields) > max(cols):
                titlefield = tdfields[cols[0]]
                byfield_a = tdfields[cols[1]]
                byfield_b = tdfields[cols[2]]
                datefield = tdfields[cols[3]]

                title_link = titlefield.find("a")
                title = titlefield.get_text().strip(" \"").strip()
                datetext = datefield.get_text().strip()
                date = get_date(datetext) or "????"

                if title_link:
                    suffix = title_link.get("href").split("/")[-1].strip()
                    info = fetch_info(suffix)
                    description = info['extract']
                else:
                    description = ""

                description = description.strip() + "\n\n" + \
                              "Studio: " + byfield_a.get_text().strip(".").strip() + ".\n\n" + \
                              "Cinematographer: " + byfield_b.get_text().strip(".").strip() + ".\n"
                description = REFSTRIPPER.sub(u"", description)

                sid = "movie: {} ({})".format(title, date[:4])
                sid = re.sub("[^\w:() ]", "", sid)
                yield webobject.Story(
                    name=sid,
                    title=title,
                    description=description,
                    date=date,
                )


def find_episodes_st1(url, season_offsset, prefix, tableclass="wikitable", cols=(1, 3, 4, 6), isterse=False,
                      table_offset=0, singleseason=False):
    """

    :param url:
    :param season_offsset:
    :param prefix:
    :param tableclass:
    :param cols:
        index of columns (title, director, author, date)
        counts only <td> and not <th>
    :param isterse:
        By default we expect every other row in the list to contain a description that go along with the preceding
        row's information. If the description row is not present, set this flag.
    :return:
    """
    with urllib.request.urlopen(url) as response:
        data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    sidcounter = defaultdict(int)
    descriptionfield = None

    for idx, table in enumerate(soup.find_all("table", class_=tableclass)):
        if idx < table_offset:
            continue
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
                adjcols = [c-coloffset for c in cols]
                #titlefield = tdfields[adjcols[0]]
                #directorfield = tdfields[adjcols[1]] if adjcols[1] > 0 else ''
                #authorfield = tdfields[adjcols[2]] if adjcols[2] > 0 else ''
                #datefield = tdfields[adjcols[3]] if adjcols[2] > 0 else ''
                (titlefield, directorfield, authorfield, datefield) = [(tdfields[c] if c >= 0 else '') for c in adjcols]

                title_link = titlefield.find("a")
                title = titlefield.get_text().strip(" \"")
                datetext = datefield.get_text().strip()
                author = "Story by: " + get_author(authorfield) if cols[2] > 0 else ''
                director = "Directed by: " + directorfield.get_text() if cols[1] > 0 else ''
                date = get_date(datetext)

                # find episode number-in-season
                if not coloffset:
                    if singleseason:
                        epfield = row.find("th").get_text()
                    else:
                        epfield = row.find("td").get_text()

                # sys.stderr.write(str(authorfield).decode("utf-8").encode("ascii", "ignore") + "\n")
                # f = authorfield
                # pdb.set_trace()

                for match in re.findall("(\d+)([a-z]*)", epfield):
                    nepid, sepid = int(match[0]), match[1]
                    if singleseason:
                        sid = prefix + "%02d%s" % (nepid, sepid)
                    else:
                        sid = prefix + "%sx%02d%s" % (idx - table_offset + season_offsset, nepid, sepid)
                    sids.append(sid)

                if isterse and title_link:
                    suffix = title_link.get("href").split("/")[-1].strip()
                    info = fetch_info(suffix)
                    description = info['extract']

                titlestack.append((sid, title, director, author, date))
                #print("ADD", titlestack[-1])

            else:
                descriptionfield = row.find("td", class_="description")
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
                    #print("POP", titlestack[0])
                    sid, title, director, author, date = titlestack.popleft()
                    sidcounter[sid] += 1
                    if numstories > 1:
                        sid += chr(ord("a") + sidcounter[sid] - 1)
                    description = description.strip()
                    if author or director:
                        description = description + "\n\n"
                        if director:
                            description += director.strip(".")
                            if author:
                                description += ". "
                        if author:
                            description += author.strip(".")
                        description += ".\n"
                    description = REFSTRIPPER.sub(u"", description)

                    yield webobject.Story(
                        name=sid,
                        title=title,
                        description=description,
                        date=date,
                    )

                sids = []
                description = ''


def title_fix(title):
    title = title.strip()
    patts = [
        r".*(- Wikipedia)$",
        r".*(\(\d+ film\))$",
    ]
    for p in patts:
        m = re.match(p, title)
        if m:
            title = title[:-len(m.group(1))]
            title = title.strip()

    return title


def find_table_story_entries(url, prefix="", tableclass="wikitable", cols=(1, 3, 4, 6), table_idxs=[0]):
    """

    :param url:
    :param season_offsset:
    :param prefix:
    :param tableclass:
    :param cols:
        index of columns (title, director, author, date)
        counts only <td> and not <th>
    :param isterse:
        By default we expect every other row in the list to contain a description that go along with the preceding
        row's information. If the description row is not present, set this flag.
    :return:
    """
    with urllib.request.urlopen(url) as response:
        data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    sidcounter = defaultdict(int)
    descriptionfield = None

    for idx, table in enumerate(soup.find_all("table", class_=tableclass)):
        if idx not in table_idxs:
            continue
        sids = []
        description = None
        titlestack = deque()
        coloffsetstack = deque()

        for ridx, row in enumerate(table.find_all("tr")):
            if ridx < 2:
                continue
            tdfields = row.find_all(["td", "th"])

            # no rowspan cols may be in between the indexes given with the "cols" argument, or things will break
            coloffset = coloffsetstack.popleft() if coloffsetstack else 0
            for td in tdfields[:min(cols)]:
                rowspan = int(td.attrs.get('rowspan', 0)) - 1
                while len(coloffsetstack) < rowspan:
                    coloffsetstack.append(0)
                for ii in range(rowspan):
                    coloffsetstack[ii] += 1

            if len(tdfields) > max(cols) - coloffset:
                adjcols = [c-coloffset for c in cols]
                prev = titlestack[-1] if titlestack else ['', '', '', '']
                (titlefield, directorfield, authorfield, datefield) = [(tdfields[c] if c >= 0 else prev[cidx+1]) for cidx, c in enumerate(adjcols)]

                title_link = titlefield.find("a")
                title = titlefield.get_text().strip(" \"").strip()
                datetext = datefield if isinstance(datefield, (str, int)) else datefield.get_text().strip()
                author = "Story by: " + get_author(authorfield) if cols[2] > 0 else ''
                director = "Directed by: " + directorfield.get_text() if cols[1] > 0 else ''
                date = get_date(datetext)

                # sys.stderr.write(str(authorfield).decode("utf-8").encode("ascii", "ignore") + "\n")
                # f = authorfield
                # pdb.set_trace()

                if title_link:
                    suffix = title_link.get("href").split("/")[-1].strip()
                    info = fetch_info(suffix)
                    description = info['extract']

                titlestack.append(("", title, director, author, date))
                print("ADD", titlestack[-1])
                yield webobject.Story(
                    name=prefix + title,
                    title=title,
                    description=description,
                    date=date,
                )




