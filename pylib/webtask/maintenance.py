import log
import subprocess
import os
import glob
import json
import urllib2
import lib.commits
import re
import credentials


def solr_commit():
    url = credentials.SOLR_URL
    try:
        import pysolr
    except ImportError:
        log.debug("pysolr not present, skipping indexing")
        return

    sanitizer = re.compile(ur'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]')
    patterns = {
        'story': os.path.join(credentials.TEMP_PATH, 'webjson/storydefinitions/*.json'),
        'theme': os.path.join(credentials.TEMP_PATH, 'webjson/themedefinitions/*.json'),
    }
    for key, pattern in patterns.iteritems():
        solr = pysolr.Solr(url + 'tstp' + key, timeout=10)
        objs = []
        for fn in glob.glob(pattern):
            if len(objs) > 100:
                solr.add(objs)
                objs = []
            with open(fn) as fh:
                obj = json.load(fh)
                for kk in obj:
                    obj[kk] = sanitizer.sub(u' ', obj[kk])
                blob = '\n\n'.join(sorted(obj.itervalues()))
                obj['_text_'] = blob
                objs.append(obj)
        solr.add(objs)

    # rebuild dictionaries
    # suggester was not activated after Jan2020 rebuild
    #urllib2.urlopen(url + 'tstptheme/suggest?suggest.build=true&suggest.dictionary=completer')
    urllib2.urlopen(url + 'tstptheme/spell?spellcheck.build=true')
    urllib2.urlopen(url + 'tstpstory/spell?spellcheck.build=true')


def main():
    log.debug("START lib.commits.dbstore_commit_data")
    lib.commits.dbstore_commit_data(recreate=False, quieter=True)
    log.debug("START solr commit")
    solr_commit()

    if False and os.name != 'nt' and os.path.isdir('/usr/local/solr'):
        log.debug("INDEX using Solr command line")
        delcmd = "curl %ststp/update?commit=true -H \"Content-Type: text/xml\" --data-binary '<delete><query>*:*</query></delete>'" % credentials.SOLR_URL
        subprocess.call(delcmd, shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/storydefinitions/*.json", shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/themedefinitions/*.json", shell=True)


