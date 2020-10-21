"""
Name:           tests/lib/textformat.py
Description:    The purpose of this file is to test functions for formatting text associated with
                theme, story, and collection objects.
"""
import lib.textformat
import unittest

class TestTextFormat(unittest.TestCase):
    def test_remove_word_wrap_column_width_newlines(self):
        #' check each single newline character in string is replaced by a space, while any two
        #' consecutive newline characters are left unmolested; this does not apply to newline
        #' characters occurring at the end of the string as they are all stripped
        input_text = "The sea\nis high\n\nagain today,\n\nwith a thrilling\nflush of wind.\n"
        expected_text = "The sea is high\n\nagain today,\n\nwith a thrilling flush of wind."
        output_text = lib.textformat.remove_word_wrap_column_width_newlines(input_text)
        self.assertEqual(output_text, expected_text)

def main():
    unittest.main(verbosity=2)
