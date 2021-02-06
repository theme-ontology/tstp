# Copyright 2021, themeontology.org
import unittest
import themeontology
import credentials
import os.path
import sys
import lib.log


class TestCache(unittest.TestCase):
    def setUp(self):
        print("")
        for path in sys.path:
            if os.path.isfile(os.path.join(path, "themeontology.py")):
                lib.log.info("Project Path: %s", path)

    def test_all(self):
        """
        Read all data in main themeing repo.
        """
        path = os.path.join(credentials.GIT_THEMING_PATH, "notes")
        to = themeontology.read(path)
        for warning in to.validate():
            print(warning.encode("ascii", "replace"))


def main():
    unittest.main(verbosity=2)
