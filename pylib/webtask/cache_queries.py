import log
import webquerylib
import sys


def main():
    if sys.argv[-1] == "build-heavy":
        log.debug("START build_heavey_visualizations")
        webquerylib.build_heavey_visualizations()
        return

    log.debug("START cache_special_queries")
    webquerylib.cache_special_queries()
    log.debug("START cache_objects")
    webquerylib.cache_objects()
    log.debug("START cache_visualizations")
    webquerylib.cache_visualizations()
