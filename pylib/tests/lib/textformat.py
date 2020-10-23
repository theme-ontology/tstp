"""
Name:           tests/lib/textformat.py
Description:    The purpose of this file is to test functions for formatting text associated with
                theme, story, and collection objects.
"""
import lib.textformat
import unittest

class TestTextFormat(unittest.TestCase):
    def test_remove_wordwrap(self):
        #' check that linebreaks (i.e. single newlines "\n") are removed from string, but that
        #' paragraph breaks (i.e. double newlines "\n\n") are left unmolested
        input_text = "The sea\nis high\n\nagain today,\n\nwith a thrilling \nflush of wind.\n"
        expected_text = "The sea is high\n\nagain today,\n\nwith a thrilling flush of wind."
        output_text = lib.textformat.remove_wordwrap(input_text)
        self.assertEqual(output_text, expected_text)

    def test_add_wordwrap(self):
        #' check that linebreaks (i.e. single newlines "\n") are added to string at regular
        #' intervals
        input_text = ("The sea is high again today, with a thrilling flush of wind. In the midst\n"
        "of winter you can feel the inventions of spring. A sky of hot nude pearl until midday,\n"
        "crickets in sheltered places, and now the wind unpacking the great planes, ransacking\n"
        "the great plains...\n\n"
        "I have escaped to this island with a few books and the child --- Melissa's child.\n")
        expected_text = ("The sea is high again today, with a thrilling\n"
        "flush of wind. In the midst of winter you can feel\n"
        "the inventions of spring. A sky of hot nude pearl\n"
        "until midday, crickets in sheltered places, and\n"
        "now the wind unpacking the great planes,\n"
        "ransacking the great plains...\n\n"
        "I have escaped to this island with a few books and\n"
        "the child --- Melissa's child.\n")
        output_text = lib.textformat.add_wordwrap(input_text, wrap_length=50)
        self.assertEqual(output_text, expected_text)

def main():
    unittest.main(verbosity=2)
