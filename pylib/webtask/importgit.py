import cgitb; cgitb.enable()
from credentials import GIT_THEMING_PATH
import os
import os.path
import webtask.test_formatting


def main():
    path = os.path.join(GIT_THEMING_PATH, "notes")
    webtask.test_formatting.main()  # will fail on serious data problems
    os.system("pyrun util.db clear nowarn")
    os.system("pyrun util.db import %s" % path)



