import credentials
import os
import m4.tasks
from webtask.common import run_task


def main():
    with m4.tasks.ctx():
        gitpath = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
        run_task("updaterepo")
        import webtask.test_formatting
        webtask.test_formatting.NOTESPATH = gitpath
        webtask.test_formatting.main()
        import webtask.test_integrity
        webtask.test_integrity.NOTESPATH = gitpath
        webtask.test_integrity.main()
