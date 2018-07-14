import unittest
import webdb


class TestCache(unittest.TestCase):
    def test_get_collections(self):
        colls = webdb.get_collections()
        self.assertIsInstance(colls, dict)

    
