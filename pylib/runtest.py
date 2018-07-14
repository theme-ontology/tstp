import sys
import unittest


def main():
    module = sys.argv[2]
    argv = sys.argv[2:]
    unittest.main(verbosity=2, module=module, argv=argv)



