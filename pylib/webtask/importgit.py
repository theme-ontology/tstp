import cgitb; cgitb.enable()
import credentials
import os
import os.path
import webtask.test_formatting


def main():
    path = os.path.join(credentials.GIT_THEMING_PATH_M4, "notes")
    webtask.test_formatting.main()  # will fail on serious data problems
    os.system("pyrun util.db clear nowarn")
    os.system("pyrun util.db import %s" % path)



