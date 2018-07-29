import log
import webquerylib


def main():
    log.debug("START cache_special_queries")
    webquerylib.cache_special_queries()
    log.debug("START cache_objects")
    webquerylib.cache_objects()

