import unittest
import tempfile
import os

import lib.dataparse
import lib.log
import logging

logging.basicConfig(level = logging.DEBUG)
lib.log.printfunc = logging.debug


class TestThemes(unittest.TestCase):
    def setUp(self):
        fh = tempfile.NamedTemporaryFile(delete=False)
        self.fn_txt = fh.name
        fh.write("""
identifier1
===========

:: Description
stuff

:: Parents
parent1
parent2

:: unknown_field
unknown
        """)
        fh.close()

    def tearDown(self):
        os.unlink(self.fn_txt)

    def test_txt(self):
        themes = list(lib.dataparse.read_themes_from_txt(self.fn_txt))
        lib.log.debug("read %s themes", len(themes))
        theme = themes[0]
        self.assertEqual(len(themes), 1)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertEqual(theme.description.strip(), "stuff")
        self.assertEqual(theme.list_parents(), ["parent1", "parent2"])

    def test_db(self):
        n = 5
        themes = list(lib.dataparse.read_themes_from_db(limit=n))[:n]
        lib.log.debug("read %s themes", len(themes))
        theme = themes[0]
        self.assertEqual(len(themes), n)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertTrue(hasattr(theme, "description"))
        self.assertTrue(hasattr(theme, "parents"))


class TestStories(unittest.TestCase):
    def setUp(self):
        fh = tempfile.NamedTemporaryFile(delete=False)
        self.fn_txt = fh.name
        fh.write("""
identifier1
===========

:: Title
sometitle

:: Release Date
1981-04-15

:: Description
somedescription

:: unknown_field
    unknown
        """)
        fh.close()

    def tearDown(self):
        os.unlink(self.fn_txt)

    def test_txt(self):
        stories = list(lib.dataparse.read_stories_from_txt(self.fn_txt))
        lib.log.debug("read %s stories...", len(stories))
        story = stories[0]
        self.assertEqual(len(stories), 1)
        self.assertFalse(hasattr(stories, "unknown_field"))
        self.assertEqual(story.title.strip(), "sometitle")
        self.assertEqual(story.description.strip(), "somedescription")
        self.assertEqual(story.date.strip(), "1981-04-15")

    def test_db(self):
        n = 5
        stories = list(lib.dataparse.read_stories_from_db(limit=n))[:n]
        lib.log.debug("read %s stories...", len(stories))
        story = stories[0]
        self.assertEqual(len(stories), n)
        self.assertFalse(hasattr(story, "unknown_field"))
        self.assertTrue(hasattr(story, "title"))
        self.assertTrue(hasattr(story, "description"))
        self.assertTrue(hasattr(story, "date"))


class TestStoryThemes(unittest.TestCase):
    def setUp(self):
        fh = tempfile.NamedTemporaryFile(delete=False)
        self.fn_txt = fh.name
        fh.write("""
identifier1
===========

:: Ratings
4 <Mikael>

:: Choice Themes
t1 [some, comment], t2

:: Major Themes
t3

:: Minor Themes
t4, t5 [another, comment]

:: unknown_field
    unknown
        """)
        fh.close()

    def tearDown(self):
        os.unlink(self.fn_txt)

    def test_txt(self):
        objs = list(lib.dataparse.read_storythemes_from_txt(self.fn_txt))
        lib.log.debug("read %s story-themes", len(objs))
        self.assertEqual(len(objs), 5)
        obj = objs[0]
        self.assertEqual(obj.name1, "identifier1")
        self.assertEqual(obj.name2, "t1")
        self.assertEqual(obj.weight, "choice")
        self.assertEqual(obj.motivation, "some, comment")
        obj = objs[4]
        self.assertEqual(obj.name1, "identifier1")
        self.assertEqual(obj.name2, "t5")
        self.assertEqual(obj.weight, "minor")
        self.assertEqual(obj.motivation, "another, comment")

    def test_db(self):
        n = 5
        objs = list(lib.dataparse.read_storythemes_from_db(limit=n))[:n]
        lib.log.debug("read %s story-themes", len(objs))
        st = objs[0]
        self.assertEqual(len(objs), n)
        self.assertFalse(hasattr(st, "unknown_field"))
        self.assertTrue(hasattr(st, "name1"))
        self.assertTrue(hasattr(st, "name2"))
        self.assertTrue(hasattr(st, "weight"))
        self.assertTrue(hasattr(st, "motivation"))


def main():
    unittest.main(verbosity=2)

