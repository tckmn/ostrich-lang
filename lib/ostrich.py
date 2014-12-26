#!/usr/bin/env python3

from collections import defaultdict
import re

# utility methods and constants
NULLRE = re.compile('')
def Enum(**enums): return type('Enum', (), enums)


class Ostrich:
    # to differentiate blocks and strings
    class Block(str): pass

    class Stack(list):
        # all Ostrich types; also used for state management
        TYPES = Enum(NUMBER=0, STRING=1, REGEXP=2, BLOCK=3, ARRAY=4)
        # extra states (used for :, etc.)
        XSTATE = Enum(ASSIGN='_XASGN', RETRIEVE='_XRETR')

        def typeof(x):
            xt = type(x)
            if xt is list:
                return OST.ARRAY
            if xt is Ostrich.Block:
                return OST.BLOCK
            if xt is type(NULLRE):
                return OST.REGEXP
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
            if to_type == OST.REGEXP:
                return re.compile(OS.tostr(x))
            if to_type == OST.STRING:
                if from_type == OST.ARRAY:
                    return ' '.join(map(OS.convert, x))
                if from_type == OST.REGEXP:
                    return x.pattern
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
            if xt == OST.REGEXP:
                return '`%s`' % x.pattern
            if xt == OST.STRING:
                return '"%s"' % x
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

        def whitespace(self, stk, state):
            pass
        INSTRUCTIONS['\n'] = whitespace
        INSTRUCTIONS[' '] = whitespace

        def negate(self, stk, state):
            x = stk.pop()
            if x in [0, '', NULLRE, Ostrich.Block(''), []]:
                stk.append(1)
            else:
                stk.append(0)
        INSTRUCTIONS['!'] = negate

        def quote(self, stk, state):
            return OST.STRING
        INSTRUCTIONS['"'] = quote

        # TODO #

        # TODO $

        # TODO %

        # TODO &

        def inspect(self, stk, state):
            stk.append(OS.inspect(stk.pop()))
        INSTRUCTIONS['\''] = inspect

        def leftparen(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.REGEXP, OST.STRING]:
                pass  # TODO uncons
            if xt == OST.BLOCK:
                pass  # TODO ???
            if xt == OST.NUMBER:
                stk.append(x - 1)
        INSTRUCTIONS['('] = leftparen

        def rightparen(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.REGEXP, OST.STRING]:
                pass  # TODO right-uncons
            if xt == OST.BLOCK:
                pass  # TODO ???
            if xt == OST.NUMBER:
                stk.append(x + 1)
        INSTRUCTIONS['('] = rightparen

        # TODO *

        def plus(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])
            if ptype == OST.ARRAY:
                stk.append(OS.convert(a, OST.ARRAY) + OS.convert(b, OST.ARRAY))
            elif ptype == OST.BLOCK:
                stk.append(Ostrich.Block(OS.tostr(a) + OS.tostr(b)))
            elif ptype == OST.REGEXP:
                stk.append(re.compile(OS.tostr(a) + OS.tostr(b)))
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
            if xt == OST.REGEXP:
                stk.append(len(x.pattern))
            if xt == OST.BLOCK:
                pass  # TODO select
            if xt == OST.NUMBER:
                stk.append(list(range(x))
        INSTRUCTIONS[','] = comma

        # TODO (this is just plus copy/pasted)
        def minus(self, stk, state):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])
            if ptype == OST.ARRAY:
                stk.append(OS.convert(a, OST.ARRAY) + OS.convert(b, OST.ARRAY))
            elif ptype == OST.BLOCK:
                stk.append(Ostrich.Block(OS.tostr(a) + OS.tostr(b)))
            elif ptype == OST.REGEXP:
                stk.append(re.compile(OS.tostr(a) + OS.tostr(b)))
            elif ptype == OST.STRING:
                stk.append(OS.tostr(a) + OS.tostr(b))
            elif ptype == OST.NUMBER:
                stk.append(a + b)
        INSTRUCTIONS['-'] = minus

        def duplicate(self, stk, state):
            stk.append(stk[-1])
        INSTRUCTIONS['.'] = duplicate

        # TODO /

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
            stk.pop()
        INSTRUCTIONS[';'] = pop

        # TODO <

        # TODO =

        # TODO >

        # TODO ?

        def roll(self, stk, state):
            count = stk.pop()
            xs = stk.popn(count)
            stk.extend(xs[1:])
            stk.append(xs[0])
        INSTRUCTIONS['@'] = roll

        # TODO A-Z

        def leftbracket(self, stk, state):
            return OST.ARRAY
        INSTRUCTIONS['['] = leftbracket

        def swaptwo(self, stk, state):
            stk.extend([stk.pop(), stk.pop()])
        INSTRUCTIONS['\\'] = swaptwo

        def rightbracket(self, stk, state):
            return -OST.ARRAY
        INSTRUCTIONS[']'] = rightbracket

        # TODO ^

        # TODO _

        def backtick(self, stk, state):
            return OST.REGEXP
        INSTRUCTIONS['`'] = backtick

        # TODO a-z

        def leftcurlybracket(self, stk, state):
            return OST.BLOCK
        INSTRUCTIONS['{'] = leftcurlybracket

        # TODO |

        # this normally isn't called unless there are unmatched brackets
        # block parsing is done within Ostrich#run
        def rightcurlybracket(self, stk, state):
            return -OST.BLOCK
        INSTRUCTIONS['}'] = rightcurlybracket

        def tilde(self, stk, state):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                pass  # TODO dump
            if xt == OST.BLOCK:
                pass  # TODO eval
            if xt == OST.REGEXP:
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
        cumulstr = ''  # string, regexp, block
        nestcount = 1  # block
        markers = []   # array

        for instr in code:

            if state == OST.STRING:
                if instr == '"':
                    self.stack.append(cumulstr)
                    cumulstr = ''
                    state = None
                else:
                    cumulstr += instr

            elif state == OST.REGEXP:
                if instr == '`':
                    self.stack.append(re.compile(cumulstr))
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
        elif state == OST.REGEXP:
            self.stack.append(re.compile(cumulstr))
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
