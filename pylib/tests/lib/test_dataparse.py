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
        fh = tempfile.NamedTemporaryFile(delete = False)
        self.fn_txt = fh.name

        fh.write("""
identifier1
===========

:: Description
    stuff

:: Parents
    more stuff

:: unknown_field
    unknown
        """)
        fh.close()

    def tearDown(self):
        os.unlink(self.fn_txt)

    def test_txt(self):
        themes = list(lib.dataparse.read_themes_from_txt(self.fn_txt))

        lib.log.debug("read themes:")
        for theme in themes:
            lib.log.debug("  " + str(theme))

        theme = themes[0]
        self.assertEqual(len(themes), 1)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertEqual(theme.description, "stuff")
        self.assertEqual(theme.parents, "more stuff")

    def test_xls(self):
        path = os.path.join(os.environ['TSTPPATH'], "resources", "test_themedefinitions.xls")
        themes = list(lib.dataparse.read_themes_from_xls(path))

        lib.log.debug("read themes:")
        for theme in themes:
            lib.log.debug("  " + str(theme))

        theme = themes[0]
        self.assertEqual(len(themes), 3)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertEqual(theme.description, "stuff")
        self.assertEqual(theme.parents, "more stuff")

    def test_db(self):
        n = 5
        themes = list(lib.dataparse.read_themes_from_db(limit = n))[:n]

        lib.log.debug("read themes:")
        for theme in themes:
            lib.log.debug("  " + str(theme))

        theme = themes[0]
        self.assertEqual(len(themes), n)
        self.assertFalse(hasattr(theme, "unknown_field"))
        self.assertTrue(hasattr(theme, "description"))
        self.assertTrue(hasattr(theme, "parents"))


class TestStories(unittest.TestCase):

    def setUp(self):
        fh = tempfile.NamedTemporaryFile(delete = False)
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
        
        lib.log.debug("read stories:")
        for story in stories:
            lib.log.debug("  " + str(story))

        story = stories[0]
        self.assertEqual(len(stories), 1)
        self.assertFalse(hasattr(stories, "unknown_field"))
        self.assertEqual(story.title, "sometitle")
        self.assertEqual(story.description, "somedescription")
        self.assertEqual(story.date, "1981-04-15")

    def test_xls(self):
        path = os.path.join(os.environ['TSTPPATH'], "resources", "test_storydefinitions.xls")
        stories = list(lib.dataparse.read_stories_from_xls(path))

        lib.log.debug("read stories:")
        for story in stories:
            lib.log.debug("  " + str(story))

        story = stories[0]
        self.assertEqual(len(stories), 1)
        self.assertFalse(hasattr(stories, "unknown_field"))
        self.assertEqual(story.title, "sometitle")
        self.assertEqual(story.description, "somedescription")
        self.assertEqual(story.date, "1981-04-15")

    def test_db(self):
        n = 5
        stories = list(lib.dataparse.read_stories_from_db(limit = n))[:n]

        lib.log.debug("read stories:")
        for story in stories:
            lib.log.debug("  " + str(story))

        story = stories[0]
        self.assertEqual(len(stories), n)
        self.assertFalse(hasattr(story, "unknown_field"))
        self.assertTrue(hasattr(story, "title"))
        self.assertTrue(hasattr(story, "description"))
        self.assertTrue(hasattr(story, "date"))


class TestStoryThemes(unittest.TestCase):

    def setUp(self):
        fh = tempfile.NamedTemporaryFile(delete = False)
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
        
        lib.log.debug("read story-themes:")
        for obj in objs:
            lib.log.debug("  " + str(obj))

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

    def test_xls_compact(self):
        path = os.path.join(os.environ['TSTPPATH'], "resources", "test_storythemes_compact.xls")
        objs = list(lib.dataparse.read_storythemes_from_xls_compact(path))

        lib.log.debug("read storythemes:")
        for obj in objs:
            lib.log.debug("  " + str(obj))

        self.assertEqual(len(objs), 10)

        obj = objs[0]
        self.assertEqual(obj.name1, "story1")
        self.assertEqual(obj.name2, "ct1")
        self.assertEqual(obj.weight, "choice")
        self.assertEqual(obj.motivation, "some, comment")

        obj = objs[9]
        self.assertEqual(obj.name1, "story2")
        self.assertEqual(obj.name2, "mit3")
        self.assertEqual(obj.weight, "minor")
        self.assertEqual(obj.motivation, "comment")

    def test_db(self):
        return

        n = 5
        stories = list(lib.dataparse.read_stories_from_db(limit = n))[:n]

        lib.log.debug("read stories:")
        for story in stories:
            lib.log.debug("  " + str(story))

        story = stories[0]
        self.assertEqual(len(stories), n)
        self.assertFalse(hasattr(story, "unknown_field"))
        self.assertTrue(hasattr(story, "title"))
        self.assertTrue(hasattr(story, "description"))
        self.assertTrue(hasattr(story, "date"))


def main():
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStoryThemes)
    #unittest.TextTestRunner(verbosity = 2).run(suite)
    unittest.main(verbosity = 2)
