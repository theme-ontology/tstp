# Copyright 2021, themeontology.org
from __future__ import print_function
import unittest
import themeontology
import credentials
import os.path


class TestCache(unittest.TestCase):
    def setUp(self):
        pass

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
