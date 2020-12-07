import m4.tasks
import lib.log
from webtask.common import run_task


def main():
    pipeline = [
        "updaterepo",
        "test_integrity",
        "test_formatting",
        "importgit",
        "cache_queries",
        "indexing",  # depends on cache_queries
    ]
    with m4.tasks.ctx():
        lib.log.info("[starting import pipeline...]")
        for item in pipeline:
            if isinstance(item, str):
                code = run_task(item)
            if code != 0:
                lib.log.info("[ERROR] task finished with code %d. Exiting.", code)

        lib.log.info("[...finished import pipeline]")
