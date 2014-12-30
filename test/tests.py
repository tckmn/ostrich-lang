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
        self.expect(';1!', '0')
        self.expect(';0!', '1')

        self.expect(';`foo`!', '0')
        self.expect(';``!', '1')

        self.expect(';{foo}!', '0')
        self.expect(';{}!', '1')

        self.expect(';[`foo`]!', '0')
        self.expect(';[``]!', '0')
        self.expect(';[]!', '1')

    def test_quote(self):
        pass  # TODO

    def test_arrset(self):
        pass  # TODO

    def test_dollar(self):
        self.expect('[3 2 4 1 5]$', '[1 2 3 4 5]')
        self.expect(';[`test``tesu``tess`]$', '[`tess` `test` `tesu`]')
        self.expect(';[{a}{c}{b}]$', '[{a} {b} {c}]')
        self.expect(';[[1][3][2]]$', '[[1] [2] [3]]')
        self.expect(';[]$', '[]')

        self.expect(';`potato`$', '`aooptt`')
        self.expect(';``$', '``')

        # TODO block

        # TODO stack nth (number)

    def test_mod(self):
        pass  # TODO

    def test_bitand(self):
        pass  # TODO

    def test_inspect(self):
        pass  # TODO

    def test_leftparen(self):
        pass  # TODO

    def test_rightparen(self):
        pass  # TODO

    def test_times(self):
        pass  # TODO

    def test_plus(self):
        self.expect('[1 2][3 4]+', '[1 2 3 4]')
        self.expect(';[{foo}{bar}]{baz}+', '[{foo} {bar} {baz}]')
        self.expect(';[`foo``bar`]`baz`+', '[`foo` `bar` `baz`]')
        self.expect(';[1 2]3+', '[1 2 3]')

        self.expect(';{foo}{bar}+', '{foobar}')
        self.expect(';{foo}`bar`+', '{foobar}')
        self.expect(';{foo}1+', '{foo1}')

        self.expect(';`foo``bar`+', '`foobar`')
        self.expect(';`foo`1+', '`foo1`')

        self.expect(';2 2+', '4')

    def test_comma(self):
        pass  # TODO

    def test_minus(self):
        pass  # TODO

    def test_duplicate(self):
        self.expect('42.', '42 42')
        self.expect(';;.', '')

    def test_div(self):
        pass  # TODO

    def test_num(self):
        pass  # TODO

    def test_assign(self):
        pass  # TODO

    def test_pop(self):
        self.expect('42;', '')
        self.expect(';', '')

    def test_lt(self):
        pass  # TODO

    def test_eq(self):
        pass  # TODO

    def test_gt(self):
        pass  # TODO

    def test_question(self):
        pass  # TODO

    def test_roll(self):
        self.expect('1 2 3 4 5', '1 2 3 4 5')

        self.expect('2@', '1 2 3 5 4')
        self.expect('2@', '1 2 3 4 5')

        self.expect('3@', '1 2 4 5 3')
        self.expect('4@', '1 4 5 3 2')
        self.expect('5@', '4 5 3 2 1')
        # TODO negative rolls

    def test_leftbracket(self):
        self.expect('[1 2 3]', '[1 2 3]')
        self.expect(';[]', '[]')

        self.expect(';[1 2 3', '[1 2 3]')
        self.expect(';[', '[]')
        self.expect(';[[1[[[2[3', '[[1 [[[2 [3]]]]]]')

    def test_swaptwo(self):
        self.expect('1 2 3\\', '1 3 2')

    def test_rightbracket(self):
        self.expect('1 2 3]', '[1 2 3]')
        self.expect('1]', '[[1 2 3] 1]')
        self.expect(']', '[[[1 2 3] 1]]')

    def test_bitxor(self):
        pass  # TODO

    def test_backtick(self):
        self.expect('`foo`', '`foo`')
        self.expect(';``', '``')

        self.expect(';`foo', '`foo`')
        self.expect(';`', '``')
        # TODO escaping (not implemented)

    def test_letter_p(self):
        pass  # TODO

    def test_letter_q(self):
        pass  # TODO

    def test_letter_z(self):
        pass  # TODO

    def test_leftcurlybracket(self):
        pass  # TODO

    def test_bitor(self):
        pass  # TODO

    def test_rightcurlybracket(self):
        pass  # TODO

    def test_tilde(self):
        self.expect('1 2 3]~', '1 2 3')
        self.expect(';;;{1 1+}~', '2')
        self.expect(';`1 1+`~', '2')
        self.expect(';42~', '-42')

if __name__ == '__main__':
    unittest.main()
