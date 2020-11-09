import log
import webquerylib
import sys
import webtask.cache_data


def main():
    if sys.argv[-1] == "build-heavy":
        log.debug("START build_heavy_visualizations")
        webquerylib.build_heavy_visualizations()
        return

    log.debug("START cache_special_queries")
    webquerylib.cache_special_queries()
    log.debug("START cache_objects")
    webquerylib.cache_objects()
    log.debug("START cache_visualizations")
    webquerylib.cache_visualizations()

    log.debug("START cache_data")
    webtask.cache_data.main()

