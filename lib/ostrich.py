#!/usr/bin/env python3

from collections import defaultdict
import itertools

# utility methods
def Enum(**enums): return type('Enum', (), enums)
def uniq(s):
    # http://stackoverflow.com/q/480214/1223693
    seen = set()
    return [x for x in s if x not in seen and not seen.add(x)]


class Ostrich:
    # to differentiate blocks and strings
    class Block(str): pass

    class Stack(list):
        # all Ostrich types; also used for state management
        TYPES = Enum(NUMBER=0, STRING=1, BLOCK=2, ARRAY=3)
        # extra states (used for :, etc.)
        XSTATE = Enum(ASSIGN='_XASGN', RETRIEVE='_XRETR')

        def typeof(x):
            xt = type(x)
            if xt is list:
                return OST.ARRAY
            if xt is Ostrich.Block:
                return OST.BLOCK
            if xt is str:
                return OST.STRING
            if xt is int:
                return OST.NUMBER

        def convert(x, to_type):
            from_type = OS.typeof(x)
            if to_type == OST.ARRAY:
                if from_type == OST.ARRAY:
                    return x
                return [x]
            if to_type == OST.BLOCK:
                return Ostrich.Block(OS.tostr(x))
            if to_type == OST.STRING:
                if from_type == OST.ARRAY:
                    return ' '.join(map(OS.convert, x))
                if from_type in [OST.NUMBER, OST.STRING, OST.BLOCK]:
                    return str(x)
            if to_type == OST.NUMBER:
                return int(OS.tostr(x))

        # for convenience
        def tostr(x):
            return OS.convert(x, OST.STRING)

        def inspect(x):
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                return '[%s]' % ' '.join(map(OS.inspect, x))
            if xt == OST.BLOCK:
                return '{%s}' % x
            if xt == OST.STRING:
                return '`%s`' % x
            if xt == OST.NUMBER:
                return str(x)

        # pop n elements
        def popn(self, n):
            xs = self[-n:]
            del self[-n:]
            return xs

        # pop by precedence: take last n elements, order as specified in TYPES
        def pprec(self, n):
            return OS.byprec(self.popn(n))

        # this one just sorts by precedence
        def byprec(xs):
            return sorted(xs, key=lambda x: OS.typeof(x), reverse=True)

    def initialize_instructions():
        def unknowninstr():
            def unknowninstr_inner(self, stk, state):
                return OS.XSTATE.RETRIEVE + self
            return unknowninstr_inner
        INSTRUCTIONS = defaultdict(unknowninstr)

        # TODO things not in GS: A-Za-z_#

        def whitespace(self, stk, state):
            pass
        INSTRUCTIONS['\n'] = whitespace
        INSTRUCTIONS[' '] = whitespace

        def negate(self, stk, state):
            x = stk.pop()
            if x in [0, '', Ostrich.Block(''), []]:
                stk.append(1)
            else:
                stk.append(0)
        INSTRUCTIONS['!'] = negate

        def quote(self, stk, state):
            pass  # TODO
        INSTRUCTIONS['"'] = quote

        def dollar(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                stk.push(sorted(x))
            if xt == OST.STRING:
                stk.push(''.join(sorted(x)))
            if xt == OST.BLOCK:
                pass  # TODO sort by
            if xt == OST.NUMBER:
                stk.push(stk[-x])
        INSTRUCTIONS['$'] = dollar

        def mod(self, stk, state):
            a, b = stk.popn(2)
            ptype, stype = map(OS.typeof, OS.byprec([a, b]))
            if ptype == OST.ARRAY:
                pass  # TODO
            elif ptype == OST.BLOCK:
                pass  # TODO
            elif ptype == OST.STRING:
                if stype == OST.NUMBER:
                    pass  # TODO str[::x]
                else:
                    stk.append(list(map(list, itertools.product(a, b))))
            elif ptype == OST.NUMBER:
                stk.append(a % b)
        INSTRUCTIONS['%'] = mod

        def bitand(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable & enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x in a2])
            elif ptype == OST.BLOCK:
                pass  # TODO ???
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c in s2]))
            elif ptype == OST.NUMBER:
                stk.append(a & b)
        INSTRUCTIONS['&'] = bitand

        def inspect(self, stk, state):
            stk.append(OS.inspect(stk.pop()))
        INSTRUCTIONS['\''] = inspect

        def leftparen(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(x[1:])
                stk.append(x[0])
            if xt == OST.BLOCK:
                pass  # TODO ???
            if xt == OST.NUMBER:
                stk.append(x - 1)
        INSTRUCTIONS['('] = leftparen

        def rightparen(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(x[:-1])
                stk.append(x[-1])
            if xt == OST.BLOCK:
                pass  # TODO ???
            if xt == OST.NUMBER:
                stk.append(x + 1)
        INSTRUCTIONS['('] = rightparen

        def times(self, stk, state):
            a, b = stk.popn(2)
            ptype, stype = map(OS.typeof, OS.byprec([a, b]))
            if ptype == OST.ARRAY:
                pass  # TODO
            elif ptype == OST.BLOCK:
                pass  # TODO
            elif ptype == OST.STRING:
                if stype == OST.NUMBER:
                    stk.append(a*b if OS.typeof(a) == ptype else b*a)
                else:
                    stk.append(b.join(list(a)))
            elif ptype == OST.NUMBER:
                stk.append(a * b)
        INSTRUCTIONS['*'] = times

        def plus(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])
            if ptype == OST.ARRAY:
                stk.append(OS.convert(a, OST.ARRAY) + OS.convert(b, OST.ARRAY))
            elif ptype == OST.BLOCK:
                stk.append(Ostrich.Block(OS.tostr(a) + OS.tostr(b)))
            elif ptype == OST.STRING:
                stk.append(OS.tostr(a) + OS.tostr(b))
            elif ptype == OST.NUMBER:
                stk.append(a + b)
        INSTRUCTIONS['+'] = plus

        def comma(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(len(x))
            if xt == OST.BLOCK:
                pass  # TODO select
            if xt == OST.NUMBER:
                stk.append(list(range(x)))
        INSTRUCTIONS[','] = comma

        def minus(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable - enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x not in a2])
            elif ptype == OST.BLOCK:
                pass  # TODO ???
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c not in s2]))
            elif ptype == OST.NUMBER:
                stk.append(a - b)
        INSTRUCTIONS['-'] = minus

        def duplicate(self, stk, state):
            if stk: stk.append(stk[-1])
        INSTRUCTIONS['.'] = duplicate

        def div(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])
            if ptype == OST.ARRAY:
                pass  # TODO
            elif ptype == OST.BLOCK:
                pass  # TODO
            elif ptype == OST.STRING:
                stk.append(a.split(OS.tostr(b)))
            elif ptype == OST.NUMBER:
                stk.append(a / b)
        INSTRUCTIONS['/'] = div

        def num(self, stk, state):
            if state == OST.NUMBER:
                stk[-1] = int(str(stk[-1]) + self)
            else:
                stk.append(int(self))
            return OST.NUMBER
        for instr in '0123456789': INSTRUCTIONS[instr] = num

        def assign(self, stk, state):
            return OS.XSTATE.ASSIGN
        INSTRUCTIONS[':'] = assign

        def pop(self, stk, state):
            if stk: stk.pop()
        INSTRUCTIONS[';'] = pop

        def lt(self, stk, state):
            pass  # TODO
        INSTRUCTIONS['<'] = lt

        def eq(self, stk, state):
            pass  # TODO
        INSTRUCTIONS['='] = eq

        def gt(self, stk, state):
            pass  # TODO
        INSTRUCTIONS['>'] = gt

        def question(self, stk, state):
            pass  # TODO
        INSTRUCTIONS['?'] = question

        def roll(self, stk, state):
            count = stk.pop()
            xs = stk.popn(count)
            stk.extend(xs[1:])
            stk.append(xs[0])
        INSTRUCTIONS['@'] = roll

        def leftbracket(self, stk, state):
            return OST.ARRAY
        INSTRUCTIONS['['] = leftbracket

        def swaptwo(self, stk, state):
            stk.extend([stk.pop(), stk.pop()])
        INSTRUCTIONS['\\'] = swaptwo

        def rightbracket(self, stk, state):
            return -OST.ARRAY
        INSTRUCTIONS[']'] = rightbracket

        def bitxor(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable | enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x not in a2] +
                           [x for x in a2 if x not in a1])
            elif ptype == OST.BLOCK:
                pass  # TODO ???
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c in s2] +
                                   [c for c in s2 if c in s1]))
            elif ptype == OST.NUMBER:
                stk.append(a ^ b)
        INSTRUCTIONS['^'] = bitxor

        def backtick(self, stk, state):
            return OST.STRING
        INSTRUCTIONS['`'] = backtick

        def leftcurlybracket(self, stk, state):
            return OST.BLOCK
        INSTRUCTIONS['{'] = leftcurlybracket

        def bitor(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable | enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append(uniq(a1 + a2))
            elif ptype == OST.BLOCK:
                pass  # TODO ???
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join(uniq(s1 + s2)))
            elif ptype == OST.NUMBER:
                stk.append(a | b)
        INSTRUCTIONS['|'] = bitor

        # this normally isn't called unless there are unmatched brackets
        # block parsing is done within Ostrich#run
        def rightcurlybracket(self, stk, state):
            return -OST.BLOCK
        INSTRUCTIONS['}'] = rightcurlybracket

        def tilde(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                stk.extend(x)
            if xt == OST.BLOCK:
                pass  # TODO eval
            if xt == OST.STRING:
                pass  # TODO eval
            if xt == OST.NUMBER:
                stk.append(-x)

        return INSTRUCTIONS

    INSTRUCTIONS = initialize_instructions()

    def __init__(self):
        self.stack = OS()
        self.variables = defaultdict(lambda: None)

    def run(self, code):
        state = None
        cumulstr = ''  # string, block
        nestcount = 1  # block
        markers = []   # array

        for instr in code:

            if state == OST.STRING:
                if instr == '`':
                    self.stack.append(cumulstr)
                    cumulstr = ''
                    state = None
                else:
                    cumulstr += instr

            elif state == OST.BLOCK:
                if instr == '}':
                    nestcount -= 1
                    if nestcount == 0:
                        self.stack.append(Ostrich.Block(cumulstr))
                        cumulstr = ''
                        nestcount = 1  # reset for next time
                        state = None
                    else:
                        cumulstr += instr
                else:
                    cumulstr += instr
                    if instr == '{':
                        nestcount += 1

            elif state == OS.XSTATE.ASSIGN:
                self.variables[instr] = self.stack[-1]
                state = None

            else:
                state = Ostrich.INSTRUCTIONS[instr](instr, self.stack, state)
                if state == OST.ARRAY:
                    markers.append(len(self.stack))
                elif state == -OST.ARRAY:
                    idx = markers.pop() if markers else 0
                    self.stack.append(self.stack.popn(-idx))
                elif type(state) is str and state.startswith(OS.XSTATE.RETRIEVE):
                    x = self.variables[state[len(OS.XSTATE.RETRIEVE):]]
                    if x:
                        self.stack.append(x)
                        if OS.typeof(x) == OST.BLOCK:
                            # TODO execute if block
                            pass

        # finished parsing instr's
        # perform final cleanup

        if state == OST.STRING:
            self.stack.append(cumulstr)
        elif state == OST.BLOCK:
            self.stack.append(Ostrich.Block(cumulstr))

        while markers:
            self.stack.append(self.stack.popn(-markers.pop()))

        return ' '.join(map(OS.inspect, self.stack))

# just for convenience
OS = Ostrich.Stack
OST = Ostrich.Stack.TYPES

if __name__ == '__main__':
    import sys  # sys.exit

    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', nargs='?',
        help='path to Ostrich file to execute'
    )
    parser.add_argument(
        '-i', '--interactive', action='store_true',
        help='enter an interactive REPL instead of executing code'
    )
    parser.add_argument(
        '-e', '--exec', help='execute a string passed as an argument'
    )

    args = parser.parse_args()
    program = Ostrich()
    if args.interactive:
        # REPL
        import readline
        while True:
            # R
            try:
                code = input('>>> ')
            except (EOFError, KeyboardInterrupt):
                sys.exit('')
            # E
            rtn = program.run(code)
            # P
            print(rtn)
            # L
    elif args.exec:
        # execute code!
        program.run(args.exec)
    elif args.filename:
        # resolve path, get code
        import os
        path = os.path.abspath(args.filename)
        if not os.path.exists(path):
            sys.exit('Err: Path %s does not exist' % path)
        code = open(path).read()

        # execute code!
        program.run(code)
    else:
        parser.print_help()
