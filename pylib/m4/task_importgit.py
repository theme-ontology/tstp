import os
import m4.tasks
import lib.log


def run_task(taskname):
    """
    pyrun webtask.taskname
    """
    cmd = "pyrun webtask.%s" % taskname
    lib.log.info("executing: %s", cmd)
    code = os.system(cmd)
    lib.log.info("command finished with code %s", code)
    return code


def main():
    # python git library whines about missing executable
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
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
