# Copyright 2023, themeontology.org
# Tests:
import pymysql
import gzip
import pickle
from autocorrect import Speller
import re
from collections import defaultdict
from itertools import chain, combinations, product
from ontologyexplorer.models import Story, Theme
from unidecode import unidecode
import totolo.deployment


RE_WORD = "[^\W_]+"
SAFE_WORDS = {"the", "to", "too", "for", "of"}


def _powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def do(query, indexname, queryoptions, obj):
    with gzip.open("/code/tmp/totolo_corpus.pickle.gz", "r") as fh:
        corpus = pickle.load(fh)
        spell = Speller(nlp_data=corpus)
    with gzip.open("/code/tmp/totolo_diacritics.pickle.gz", "r") as fh:
        diacritics = pickle.load(fh)
        dspell = Speller(nlp_data=diacritics)
    conn = pymysql.connect(
        host=totolo.deployment.SPHINX.HOST,
        port=totolo.deployment.SPHINX.PORT,
        user='', passwd='', charset='utf8', db='',
    )
    cur = conn.cursor()

    if re.search('[\\(\\)"]', query):
        qry = "SELECT *, WEIGHT() FROM {} WHERE MATCH( %(query)s ) LIMIT 100 OPTION {}".format(indexname, queryoptions)
        cur.execute(qry, {"query": query})
        result = list(cur)
    else:
        words = re.findall(RE_WORD, query)
        acwords = []
        for word in words:
            acw = word
            if word not in SAFE_WORDS:
                acw = spell.autocorrect_word(word)
                if word == acw:
                    dword = unidecode(word)
                    ac_dword = dspell.autocorrect_word(dword)
                    suggestions = diacritics.get(ac_dword, set([word]))
                    if suggestions:
                        acw = suggestions.pop()
            acwords.append([word, acw] if acw != word else [word])
            # TODO: wrap this in error handling as autocorrect is unlikely to be robust
        if len(acwords) < 5:
            delta_result = defaultdict(float)
            for wordset in _powerset(acwords):
                print(wordset)
                if wordset:
                    for wordlist in product(*wordset):
                        query = " ".join(wordlist)
                        qry = "SELECT *, WEIGHT() FROM {} WHERE MATCH( %(query)s ) LIMIT 100 OPTION {}".format(
                            indexname, queryoptions)
                        cur.execute(qry, {"query": query})
                        for idx, weight in cur:
                            score = weight * (2 ** len(wordset) - 1)
                            delta_result[idx] = max(delta_result[idx], score)
            result = sorted(delta_result.items(), reverse=True)
        else:
            query = '"{}"/1'.format(" ".join(words + [x[1] for x in acwords if len(x) > 1]))
            qry = "SELECT *, WEIGHT() FROM {} WHERE MATCH( %(query)s ) LIMIT 100 OPTION {}".format(indexname, queryoptions)
            cur.execute(qry, {"query": query})
            result = list(cur)

    idx2weight = dict(result)
    maxw = max(idx2weight.values()) if idx2weight else 0
    objects = obj.objects.filter(idx__in=idx2weight.keys())
    if maxw > 0:
        for idx in idx2weight:
            idx2weight[idx] = int(idx2weight[idx] / maxw * 100)

    # Sphinx' scoring sucks so we have to boost words that are matched in the title
    # to not yield certain silly result oversights.
    word_in_name = defaultdict(set)
    fieldattr = "name" if indexname == "totolo_themes" else "title"
    for obj in objects:
        idx = obj.idx
        for wordlist in acwords:
            for word in wordlist:
                if word in getattr(obj, fieldattr).lower().split():
                    word_in_name[idx].add(word)
                    break
    if word_in_name:
        qq = len(acwords)
        for obj in objects:
            idx = obj.idx
            name = getattr(obj, fieldattr).lower()
            if name == query:
                idx2weight[idx] = 100.0
            else:
                # Jaccard index scoring
                nn = len(name.split())
                mm = len(word_in_name[idx])
                ss = mm / (nn + qq - mm)
                idx2weight[idx] = idx2weight[idx] * 0.1 + 80.0 + 10 * ss

    objects = sorted(objects, key=lambda t: idx2weight[t.idx], reverse=True)
    return [(oo, idx2weight[oo.idx]) for oo in objects]


def themes(query):
    obj = Theme
    indexname = "totolo_themes"
    queryoptions = "field_weights=(name=10, description=1)"
    return do(query, indexname, queryoptions, obj)


def stories(query):
    obj = Story
    indexname = "totolo_stories"
    queryoptions = "field_weights=(title=5, description=1)"
    return do(query, indexname, queryoptions, obj)


