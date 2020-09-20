import unittest
import webquerylib


class TestCache(unittest.TestCase):
    def setUp(self):
        webquerylib.TARGET = "test"

    def test_special(self):
        webquerylib.cache_special_queries()

    def test_cache_object(self):
        webquerylib.cache_objects()


def main():
    unittest.main(verbosity=2)
