#!/usr/bin/python3

# namespace shenanigans
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..') + '/lib')

import ostrich, unittest


class OstrichTests(unittest.TestCase):

    def setUp(self):
        self.program = ostrich.Ostrich()

    def test_whitespace(self):
        self.assertEqual(self.program.run('   \n  \n\n'), '')

    def test_negate(self):
        self.assertEqual(self.program.run('42!'), '0')
        self.assertEqual(self.program.run(';0!'), '1')

if __name__ == '__main__':
    unittest.main()
