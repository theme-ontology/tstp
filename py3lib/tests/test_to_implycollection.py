# Copyright 2023, themeontology.org
# Tests:
import unittest
import themeontology
import os.path
import sys
import tempfile
import shutil
import lib.files
import lib.git


class TestCache(unittest.TestCase):
    def setUp(self):
        pass

    def test_all(self):
        base = os.path.join(tempfile.gettempdir(), "test_to_implycollection")
        repo = os.path.join(base, "theming")
        shutil.rmtree(base, True)
        lib.files.mkdirs(repo)
        lib.git.download_headversion("https://github.com/theme-ontology", "theming", repo)
        path = os.path.join(repo, "notes")
        to = themeontology.read(path, imply_collection=True)
        print(path)
        s = to.story["tvseries: Star Trek: The Next Generation"]
        css = s.get("Component Stories")
        print(list(css))

        #shutil.rmtree(base, True)
