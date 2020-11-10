import log
import os
import glob
import json
import urllib2
import re
import credentials

SANITIZER = re.compile(ur'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]')
PATTERNS = {
    'story': os.path.join(credentials.TEMP_PATH, 'webjson/storydefinitions/*.json'),
    'theme': os.path.join(credentials.TEMP_PATH, 'webjson/themedefinitions/*.json'),
}
metakeys = ['id']
dropkeys = ['type', 'meta', 'date', 'date2']

def iter_docs(idx):
    """
    Iterate over documents for an index.
    """
    pattern = PATTERNS[idx]
    for fn in glob.glob(pattern):
        with open(fn) as fh:
            obj = json.load(fh)
            for kk in obj:
                obj[kk] = SANITIZER.sub(u' ', obj[kk])
            blob = '\n\n'.join(sorted(obj.itervalues()))
            obj['text'] = blob
            yield obj


def solr_commit():
    url = credentials.SOLR_URL
    try:
        import pysolr
    except ImportError:
        log.debug("pysolr not present, skipping indexing")
        return

    for key, pattern in PATTERNS.iteritems():
        solr = pysolr.Solr(url + 'tstp' + key, timeout=10)
        objs = []
        for fn in glob.glob(pattern):
            if len(objs) > 100:
                solr.add(objs)
                objs = []
            with open(fn) as fh:
                obj = json.load(fh)
                for kk in obj:
                    obj[kk] = PATTERNS.sub(u' ', obj[kk])
                blob = '\n\n'.join(sorted(obj.itervalues()))
                obj['_text_'] = blob
                objs.append(obj)
        solr.add(objs)

    # rebuild dictionaries
    # suggester was not activated after Jan2020 rebuild
    #urllib2.urlopen(url + 'tstptheme/suggest?suggest.build=true&suggest.dictionary=completer')
    urllib2.urlopen(url + 'tstptheme/spell?spellcheck.build=true')
    urllib2.urlopen(url + 'tstpstory/spell?spellcheck.build=true')


def elasticsearch_commit():
    """
    Read json data cached on disk and index with elasticsearch.
    """
    es = None
    if credentials.ES_HOSTS:
        try:
            from elasticsearch import Elasticsearch
            from elasticsearch import helpers
            es = Elasticsearch(credentials.ES_HOSTS)
        except ImportError:
            pass
    if not es:
        log.debug("elasticsearch no available, skipping indexing")
        return

    def iter_actions():
        for idx in PATTERNS:
            for doc in iter_docs(idx):
                action = {'_index': idx}
                for key in metakeys:
                    if key in doc:
                        action['_' + key] = doc.pop(key)
                for key in dropkeys:
                    if key in doc:
                        del doc[key]
                action['_source'] = doc
                yield action

    for success, info in helpers.parallel_bulk(es, iter_actions(), chunk_size=100):
        if not success:
            from pprint import pprint as pp
            print('A document failed:')
            pp(info)
            return

def main():
    log.debug("START solr commit")
    solr_commit()

    log.debug("START elasticsearch commit")
    elasticsearch_commit()

