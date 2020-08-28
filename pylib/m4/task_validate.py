import credentials
import os
import m4.tasks


def main():
    with m4.tasks.ctx():
        gitpath = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
        os.chdir(gitpath)
        os.system("git pull")
        import webtask.test_formatting
        webtask.test_formatting.NOTESPATH = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
        webtask.test_formatting.main()
        import webtask.test_integrity
        webtask.test_integrity.NOTESPATH = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
        webtask.test_integrity.main()
