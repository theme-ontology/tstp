import urllib
import urllib2
import json
from collections import defaultdict
import lib.log
import itertools


URL_BASE = "http://www.themeontology.org:8983/solr/tstp"
DEBUG = False
FIELD_WEIGHT = {
    'theme': 100.0,
    'story': 100.0,
    'parents': 30.0,
    'description': 10.0,
    '_text_': 1.0,
}
MAX_VARIATIONS = 32
VALID_CORES = ['theme', 'story']


def prod(iter):
    f = lambda x, y: x * y
    return reduce(f, iter, 1)


def query(core, qtype, q):
    params = {"q": q}

    if qtype == "select":
        params.update({
            "defType": "edismax",
            "fl": core + ",score",
            "pf": " ".join("%s^%s" % (k, v) for k, v in  FIELD_WEIGHT.iteritems()),
            "rows": 1000,
        })
    elif qtype == "suggest":
        params.update({
            "suggest.dictionary": "completer",
            "rows": 10,
        })
    elif qtype == "spell":
        pass

    url = URL_BASE + core + "/" + qtype + "?" + urllib.urlencode(params)
    with lib.log.Timer(url if DEBUG else None):
        return json.load(urllib2.urlopen(url))


def find(core, q):
    """
    Perform search.
    :return:
    List of (score, item).
    """
    order = []
    weights = {}
    max_weights = {}
    replacements = []
    scores = defaultdict(int)

    q = q.strip()
    qlist = [ unicode(w.strip()) for w in q.split(" ") if w.strip() ]
    qset = set(kw.lower() for kw in qlist)
    if not qlist: return []
    if DEBUG: lib.log.debug("query list: %s", qlist)

    # find spelling variations
    spellresult = query(core, "spell", q)
    variations = spellresult['spellcheck']['suggestions']
    bykw = {kw:set() for ii, kw in enumerate(variations) if ii%2==0}
    for ii, kw in enumerate(variations):
        # ignores spelling suggestions for words with asterisks and gunk
        if ii%2 == 0 and kw.isalpha():
            for spec in variations[ii+1]['suggestion']:
                word = spec['word']
                weight = spec['freq']
                spec['kw'] = kw
                order.append(spec)
                bykw[kw].add(word)
                weights[(kw, word)] = weight
                max_weights[kw] = max(max_weights.get(kw, 0), weight)

    for kw, word in weights.keys():
        weights[(kw, word)] /= float(max_weights[kw])

    # find suggestions for completing the last word if there's no gunk in it
    kw = qlist[-1].lower()
    if kw.isalpha():
        maxweight = -1
        completeresults = query(core, "suggest", q)
        try:
            completions = completeresults["suggest"]["completer"][q]['suggestions']
        except KeyError:
            completions = []
            if DEBUG:
                lib.log.error("unexpected result from completer...")

        for ii, cspec in enumerate(completions):
            word = cspec['term'].split('\x1e')[-1]
            weight = cspec['weight']
            maxweight = max(maxweight, weight)
            if weight < maxweight / 10.0 or ii > 5: break
            spec = { 'word': word, 'freq': weight }
            order.append(spec)
            if kw not in bykw:
                bykw[kw] = set()
            bykw[kw].add(word)
            weights[(kw, word)] = weight / float(maxweight)

    order.sort(key=lambda spec: -spec['freq'])

    if DEBUG:
        for kw in sorted(bykw):
            lib.log.debug("trying variations for %s: %s", kw, sorted(bykw[kw]))

    while True:
        count = prod(len(x)+1 for x in bykw.itervalues())
        if count > MAX_VARIATIONS:
            spec = order.pop()
            bykw[spec['kw']].remove(spec['word'])
            if DEBUG:
                lib.log.debug("too many variations (%d), ignoring: %s", count, spec)
        else:
            break

    for kw, alts in bykw.iteritems():
        rl = [(kw, kw)]
        rl.extend((kw, alt) for alt in alts)
        replacements.append(rl)

    for replace_list in itertools.product(*replacements):
        basescore = 1.0
        for kw, word in replace_list:
            if kw == word:
                basescore += 1.0
            else:
                basescore += weights[(kw, word)] * 0.5
        basescore /= float(len(replace_list)) + 1
        rlu = {kw.lower(): word for kw, word in replace_list}
        nq = " ".join(rlu.get(w.lower().strip("*"), w) for w in qlist)
        result = query(core, "select", nq.encode('utf8'))['response']['docs']
        for spec in result:
            score = (basescore * spec['score']) / 10.0
            for thing in spec[core]:
                scores[thing] = max(scores.get(thing), score)

    scores = [(v, k) for k, v in scores.iteritems()]
    scores.sort(reverse=True)
    return scores



