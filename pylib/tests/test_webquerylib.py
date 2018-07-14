import unittest
import sys
import webquerylib
import lib.log


class TestCache(unittest.TestCase):
    def test_special(self):
        print webquerylib.list_special_queries()
        #webquerylib.cache_special_queries()


