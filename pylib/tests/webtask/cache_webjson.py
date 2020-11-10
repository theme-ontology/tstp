import unittest
import webquerylib
import webtask.cache_webjson


class TestCache(unittest.TestCase):
    def setUp(self):
        webquerylib.TARGET = "test"

    def test_cache_object(self):
        webtask.cache_webjson.cache_objects()


def main():
    unittest.main(verbosity=2)
