#!/usr/bin/python3

# namespace shenanigans
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..') + '/lib')

import ostrich, unittest


class OstrichTests(unittest.TestCase):

    def setUp(self):
        self.program = ostrich.Ostrich()

    def expect(self, code, result):
        self.assertEqual(self.program.run(code), result)

    def test_whitespace(self):
        self.expect('   \n  \n\n', '')

    def test_negate(self):
        self.expect('42!', '0')
        self.expect(';0!', '1')

        for delims in [('"', '"'), ('`', '`'), ('{', '}')]:
            self.expect(';%sfoo%s!' % delims, '0')
            self.expect(';%s %s!'   % delims, '0')
            self.expect(';%s%s!'    % delims, '1')

        # TODO arrays (not implemented yet)

    def test_quote(self):
        self.expect('"foo"', '"foo"')
        self.expect(';" "', '" "')
        self.expect(';""', '""')

        self.expect(';"foo', '"foo"')
        self.expect(';"', '""')
        # TODO escaping (not implemented)

    def test_dollar(self):
        pass  # TODO

    def test_inspect(self):
        pass  # TODO

    def test_leftparen(self):
        pass  # TODO

    def test_rightparen(self):
        pass  # TODO

    def test_plus(self):
        pass  # TODO

    def test_comma(self):
        pass  # TODO

    def test_minus(self):
        pass  # TODO

    def test_duplicate(self):
        pass  # TODO

    def test_num(self):
        pass  # TODO

    def test_assign(self):
        pass  # TODO

    def test_pop(self):
        pass  # TODO

    def test_roll(self):
        pass  # TODO

    def test_leftbracket(self):
        pass  # TODO

    def test_swaptwo(self):
        pass  # TODO

    def test_rightbracket(self):
        pass  # TODO

    def test_backtick(self):
        self.expect('`foo`', '`foo`')
        self.expect(';` `', '` `')
        self.expect(';``', '``')

        self.expect(';`foo', '`foo`')
        self.expect(';`', '``')
        # TODO escaping (not implemented)

    def test_leftcurlybracket(self):
        pass  # TODO

    def test_rightcurlybracket(self):
        pass  # TODO

    def test_tilde(self):
        pass  # TODO

if __name__ == '__main__':
    unittest.main()
