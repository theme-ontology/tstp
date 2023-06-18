# Copyright 2021, themeontology.org
import unittest
import themeontology
import credentials
import os.path
import sys
import lib.log


class TestCache(unittest.TestCase):
    def setUp(self):
        pass

    def test_all(self):
        """
        Read all data in main themeing repo.
        """
        print("")
        for path in sys.path:
            if os.path.isfile(os.path.join(path, "themeontology.py")):
                lib.log.info("Project Path: %s", path)
        path = os.path.join(credentials.GIT_THEMING_PATH, "notes")
        to = themeontology.read(path)
        for warning in to.validate():
            print(warning.encode("ascii", "replace"))

    def test_cycle_warning(self):
        """
        Ensure we get warnings about theme cycles.
        """
        data1 = """
AAA
===
:: Parents
AAA
        """
        data2 = """
AAA
===
:: Parents
BBB

BBB
===
:: Parents
AAA
        """
        data3 = """
AAA
===
:: Parents
BBB

BBB
===
:: Parents
CCC

CCC
===
:: Parents
AAA
        """
        to = themeontology.empty()
        to.read_themes(data1)
        self.assertEqual(len([msg for msg in to.validate() if "Cycle:" in msg]), 1)

        to = themeontology.empty()
        to.read_themes(data2)
        self.assertEqual(len([msg for msg in to.validate() if "Cycle:" in msg]), 1)

        to = themeontology.empty()
        to.read_themes(data3)
        self.assertEqual(len([msg for msg in to.validate() if "Cycle:" in msg]), 1)


def main():
    unittest.main(verbosity=2)
