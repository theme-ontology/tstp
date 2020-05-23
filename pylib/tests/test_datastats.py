import unittest
import tempfile
import os
import json

import lib.datastats
import lib.log


class TestThemes(unittest.TestCase):
    def test_get_themes_similarity_v1(self):
        print("\n")
        order, scoreslist = lib.datastats.get_themes_similarity_v1()
        serial = json.dumps((order, scoreslist))
        scores = {tuple(x[:2]) : tuple(x[2:]) for x in scoreslist}
        lib.log.debug("JSON: %s...", serial[:50])
        lib.log.debug("themes: %d", len(order))
        lib.log.debug("non-trivial scores: %d", len(scores))

        # unlikely to change much but might have to be update if hierarchy does change
        themes = ["the human condition", "romantic love", "infatuation"]
        orders = [order.index(t) for t in themes]
        for t1 in themes:
            o1 = order.index(t1)
            for t2 in themes:
                o2 = order.index(t2)
                if o1 == o2:
                    s1, s2 = 0, 0
                elif o1 > o2:
                    s2, s1 = scores[(o2, o1)]
                else:
                    s1, s2 = scores[(o1, o2)]
                lib.log.debug("    (%d, %d): '%s', '%s'", s1, s2, t1, t2)
                if (t1, t2) == ("the human condition", "romantic love"):
                    self.assertEquals((s1, s2), (0, 4))
                if (t1, t2) == ("romantic love", "infatuation"):
                    self.assertEquals((s1, s2), (0, 1))


def main():
    unittest.main(verbosity = 2)
