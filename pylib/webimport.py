import urllib2
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse



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



def json_story_from_url_webquery():
    from webphp import php_get as get
    url = get("url")
    return json_story_from_url(url)


def json_story_from_url(url=None):
    data = urllib2.urlopen(url).read()
    soup = BeautifulSoup(data, "html.parser")
    infobox = soup.find("table", class_ = "infobox")
    title = infobox.find(["td", "th"]).get_text().strip()

    word_tokens = soup.get_text().lower().split(" ")
    candidates = [
        ("movie", len([x for x in word_tokens if "film" in x])),
        ("tvepisode", len([x for x in word_tokens if "episode" in x])),
    ]
    candidates.sort(key=lambda x: x[-1])

    if not title:
        title = soup.find("title").get_text()
        title = title_fix(title)

    data = {
        'title': title,
        'references': url,
        'type': candidates[-1][0],
        'date': "????",
        'year': "????",
        'description': "",
    }

    idesc = soup.find("body").find("p", class_=lambda x: x is None, recursive=True)

    if idesc:
        desc = idesc.get_text().strip()
        desc = re.sub("\[.*?\]", "", desc)
        desc = re.sub("  +", " ", desc)
        data['description'] = desc

    if infobox:
        #print infobox.prettify()

        for tr in infobox.find_all("tr"):
            if tr.find(["th", "td"]).get_text().lower() in ("released", "release date"):
                idate = tr.find_all("td")[-1]
                idate2 = idate.find("span", class_=["bday", "published"])

                if idate2:
                    date = idate2.get_text()
                else:
                    date = idate.get_text().strip()
                date = date.split("(")[0].strip()
                data['date'] = date
                pdate = parse(date)
                data['year'] = str(pdate.year)

    return data




def main():
    from pprint import pprint as pp
    urls = [
        "https://en.wikipedia.org/wiki/Robot_Monster",
        "https://en.wikipedia.org/wiki/Avatar_(2009_film)",
        "https://en.wikipedia.org/wiki/Negadon:_The_Monster_from_Mars",
        "https://en.wikipedia.org/wiki/The_Naked_Now",
    ]
    for url in urls:
        print
        print url
        print "=" * len(url)

        resp = json_story_from_url(url)
        pp(resp)

    print

