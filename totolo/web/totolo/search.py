# Copyright 2023, themeontology.org
# Tests:
import pymysql
import credentials
import gzip
import pickle
from autocorrect import Speller
import re
from collections import defaultdict
from itertools import chain, combinations, product
from ontologyexplorer.models import Story, Theme


RE_WORD = "[^\W_]+"


def _powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def do(query, indexname, queryoptions, obj):
    with gzip.open("/code/tmp/totolo_corpus.pickle.gz", "r") as fh:
        corpus = pickle.load(fh)
        spell = Speller(nlp_data=corpus)
    conn = pymysql.connect(
        host=credentials.SERVER_SPHINX,
        port=credentials.PORT_SPHINX,
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
            acw = spell.autocorrect_word(word)
            acwords.append([word, acw] if acw != word else [word])
            # TODO: wrap this in error handling as autocorrect is unlikely to be robust
        if len(acwords) < 5:
            delta_result = defaultdict(float)
            for wordset in _powerset(acwords):
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
    objects = obj.objects.filter(idx__in=idx2weight.keys())
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


