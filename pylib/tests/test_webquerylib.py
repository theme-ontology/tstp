import unittest
import sys
import webquerylib
import lib.log


class TestCache(unittest.TestCase):
    def setUp(self):
        webquerylib.TARGET = "test"

    def test_special(self):
        webquerylib.cache_special_queries()

    def test_cache_object(self):
        webquerylib.cache_objects()

