import log
import subprocess
import os
import glob
import json
import urllib2
import lib.commits


def solr_commit():
    try:
        import pysolr
    except ImportError:
        log.debug("pysolr not present, skipping indexing")
        return

    patterns = {
        'story': '/tmp/webjson/storydefinitions/*.json',
        'theme': '/tmp/webjson/themedefinitions/*.json',
    }
    for key, pattern in patterns.iteritems():
        solr = pysolr.Solr('http://localhost:8983/solr/tstp' + key, timeout=10)
        objs = []
        for fn in glob.glob(pattern):
            if len(objs) > 100:
                solr.add(objs)
                objs = []
            with open(fn) as fh:
                obj = json.load(fh)
                blob = '\n\n'.join(obj.itervalues())
                obj['_text_'] = blob
                objs.append(obj)
        solr.add(objs)

    # rebuild dictionaries
    urllib2.urlopen('http://localhost:8983/solr/tstptheme/suggest?suggest.build=true&suggest.dictionary=completer')
    urllib2.urlopen('http://localhost:8983/solr/tstptheme/spell?spellcheck.build=true')
    urllib2.urlopen('http://localhost:8983/solr/tstpstory/spell?spellcheck.build=true')


def main():
    log.debug("START lib.commits.dbstore_commit_data")
    lib.commits.dbstore_commit_data(recreate=False, quieter=True)
    log.debug("START solr commit")
    solr_commit()

    if False and os.name != 'nt' and os.path.isdir('/usr/local/solr'):
        log.debug("INDEX using Solr command line")
        delcmd = "curl http://localhost:8983/solr/tstp/update?commit=true -H \"Content-Type: text/xml\" --data-binary '<delete><query>*:*</query></delete>'"
        subprocess.call(delcmd, shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/storydefinitions/*.json", shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/themedefinitions/*.json", shell=True)


