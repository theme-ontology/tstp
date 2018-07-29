import log
import webquerylib
import subprocess
import os


def main():
    log.debug("START cache_special_queries")
    webquerylib.cache_special_queries()
    log.debug("START cache_objects")
    webquerylib.cache_objects()

    if os.name != 'nt' and os.path.isdir('/usr/local/solr'):
        log.debug("INDEX using Solr")
        delcmd = "curl http://localhost:8983/solr/tstp/update?commit=true -H \"Content-Type: text/xml\" --data-binary '<delete><query>*:*</query></delete>'"
        subprocess.call(delcmd, shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/storydefinitions/*.json", shell=True)
        subprocess.call("/usr/local/solr/bin/post -c tstp /tmp/webjson/themedefinitions/*.json", shell=True)

