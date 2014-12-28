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
    MAJOR_VERSION = 0
    MINOR_VERSION = 1
    PATCH_VERSION = 1
    # VERSION_DESC = None
    VERSION_DESC = 'alpha'

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
            if xt is block:
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
                return block(OS.tostr(x))
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
                return '%d'   % x

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
            def unknowninstr_inner(self, stk, prgm):
                return OS.XSTATE.RETRIEVE + self
            return unknowninstr_inner
        INSTRUCTIONS = defaultdict(unknowninstr)

        # TODO things not in GS: A-Za-z_#

        def whitespace(self, stk, prgm):
            pass
        INSTRUCTIONS['\n'] = whitespace
        INSTRUCTIONS[' '] = whitespace

        def negate(self, stk, prgm):
            x = stk.pop()
            if x in [0, '', block(''), []]:
                stk.append(1)
            else:
                stk.append(0)
        INSTRUCTIONS['!'] = negate

        def quote(self, stk, prgm):
            pass  # TODO "
        INSTRUCTIONS['"'] = quote

        def dollar(self, stk, prgm):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                stk.append(sorted(x))
            if xt == OST.STRING:
                stk.append(''.join(sorted(x)))
            if xt == OST.BLOCK:
                toSort = stk.pop()
                def sKey(el):
                    prgm.run(OS.inspect(el))
                    prgm.run(x)
                    return stk.pop()
                stk.append(sorted(toSort, key=sKey))
            if xt == OST.NUMBER:
                stk.append(stk[-x])
        INSTRUCTIONS['$'] = dollar

        def mod(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == OST.ARRAY:
                if stype == OST.NUMBER:
                    stk.append(p[::s])
                elif stype == OST.STRING:
                    pass  # TODO array%string
                elif stype == OST.BLOCK:
                    marker = len(stk)
                    for x in p:
                        prgm.run(OS.inspect(x))
                        prgm.run(s)
                    stk.append(stk[marker:])
                    del stk[marker:-1]
                else:
                    split = []
                    prevIdx = 0
                    for i in range(len(a) - len(b) + 1):
                        if a[i:i+len(b)] == b:
                            split.append(a[prevIdx:i])
                            prevIdx = i + len(b)
                    split.append(a[prevIdx:])
                    stk.append(list(filter(None, split)))
            elif ptype == OST.BLOCK:
                if stype == OST.NUMBER:
                    pass  # TODO block/number
                elif stype == OST.STRING:
                    marker = len(stk)
                    for x in s:
                        prgm.run(OS.inspect(x))
                        prgm.run(p)
                    stk.append(''.join(stk[marker:]))
                    del stk[marker:-1]
                else:
                    pass  # TODO block/block
            elif ptype == OST.STRING:
                if stype == OST.NUMBER:
                    stk.append(p[::s])
                else:
                    stk.append(list(filter(None, a.split(b))))
            elif ptype == OST.NUMBER:
                stk.append(a % b)
        INSTRUCTIONS['%'] = mod

        def bitand(self, stk, prgm):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable & enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x in a2])
            elif ptype == OST.BLOCK:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(block(''.join([c for c in s1 if c in s2])))
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c in s2]))
            elif ptype == OST.NUMBER:
                stk.append(a & b)
        INSTRUCTIONS['&'] = bitand

        def inspect(self, stk, prgm):
            stk.append(OS.inspect(stk.pop()))
        INSTRUCTIONS['\''] = inspect

        def leftparen(self, stk, prgm):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(x[1:])
                stk.append(x[0])
            if xt == OST.BLOCK:
                pass  # TODO block(
            if xt == OST.NUMBER:
                stk.append(x - 1)
        INSTRUCTIONS['('] = leftparen

        def rightparen(self, stk, prgm):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(x[:-1])
                stk.append(x[-1])
            if xt == OST.BLOCK:
                pass  # TODO block)
            if xt == OST.NUMBER:
                stk.append(x + 1)
        INSTRUCTIONS[')'] = rightparen

        def times(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == OST.ARRAY:
                if stype == OST.NUMBER:
                    stk.append(p * s)
                elif stype == OST.STRING:
                    stk.append(s.join(map(OS.inspect, p)))
                elif stype == OST.BLOCK:
                    stk.append(p[0])
                    for x in p[1:]:
                        stk.append(x)
                        prgm.run(s)
                else:
                    joined = [a[0]]
                    for el in a[1:]: joined.extend(b + [el])
                    stk.append(joined)
            elif ptype == OST.BLOCK:
                if stype == OST.NUMBER:
                    for _ in range(s):
                        prgm.run(p)
                elif stype == OST.STRING:
                    stk.append(s[0])
                    for x in s[1:]:
                        stk.append(x)
                        prgm.run(p)
                else:
                    pass  # TODO block*block
            elif ptype == OST.STRING:
                if stype == OST.NUMBER:
                    stk.append(p * s)
                else:
                    stk.append(b.join(list(a)))
            elif ptype == OST.NUMBER:
                stk.append(a * b)
        INSTRUCTIONS['*'] = times

        def plus(self, stk, prgm):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])
            if ptype == OST.ARRAY:
                stk.append(OS.convert(a, OST.ARRAY) + OS.convert(b, OST.ARRAY))
            elif ptype == OST.BLOCK:
                stk.append(block(OS.tostr(a) + OS.tostr(b)))
            elif ptype == OST.STRING:
                stk.append(OS.tostr(a) + OS.tostr(b))
            elif ptype == OST.NUMBER:
                stk.append(a + b)
        INSTRUCTIONS['+'] = plus

        def comma(self, stk, prgm):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt in [OST.ARRAY, OST.STRING]:
                stk.append(len(x))
            if xt == OST.BLOCK:
                toSelect = stk.pop()
                arr = []
                for item in toSelect:
                    prgm.run(OS.inspect(item))
                    prgm.run(x)
                    if stk.pop():
                        arr.append(item)
                stk.append(arr)
            if xt == OST.NUMBER:
                stk.append(list(range(x)))
        INSTRUCTIONS[','] = comma

        def minus(self, stk, prgm):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable - enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x not in a2])
            elif ptype == OST.BLOCK:
                pass  # TODO
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c not in s2]))
            elif ptype == OST.NUMBER:
                stk.append(a - b)
        INSTRUCTIONS['-'] = minus

        def duplicate(self, stk, prgm):
            if stk: stk.append(stk[-1])
        INSTRUCTIONS['.'] = duplicate

        def div(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == OST.ARRAY:
                if stype == OST.NUMBER:
                    stk.append([p[i:i+s] for i in range(0, len(p), s)])
                elif stype == OST.STRING:
                    pass  # TODO array/string
                elif stype == OST.BLOCK:
                    for x in p:
                        prgm.run(OS.inspect(x))
                        prgm.run(s)
                else:
                    split = []
                    prevIdx = 0
                    for i in range(len(a) - len(b) + 1):
                        if a[i:i+len(b)] == b:
                            split.append(a[prevIdx:i])
                            prevIdx = i + len(b)
                    split.append(a[prevIdx:])
                    stk.append(split)
            elif ptype == OST.BLOCK:
                if stype == OST.NUMBER:
                    pass  # TODO block/number
                elif stype == OST.STRING:
                    for x in s:
                        prgm.run(OS.inspect(x))
                        prgm.run(p)
                else:
                    pass  # TODO block/block
            elif ptype == OST.STRING:
                stk.append(p.split(OS.tostr(s)))
            elif ptype == OST.NUMBER:
                stk.append(a / b)
        INSTRUCTIONS['/'] = div

        def num(self, stk, prgm):
            if prgm.state == OST.NUMBER:
                stk[-1] = int(str(stk[-1]) + self)
            else:
                stk.append(int(self))
            return OST.NUMBER
        for instr in '0123456789': INSTRUCTIONS[instr] = num

        def assign(self, stk, prgm):
            return OS.XSTATE.ASSIGN
        INSTRUCTIONS[':'] = assign

        def pop(self, stk, prgm):
            if stk: stk.pop()
        INSTRUCTIONS[';'] = pop

        def lt(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == stype:
                stk.append(int(a < b))
            else:
                if stype == OST.NUMBER:
                    stk.append(OS.convert(p[:s], ptype))
                else:
                    pass  # TODO
        INSTRUCTIONS['<'] = lt

        def eq(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == stype:
                stk.append(int(a == b))
            else:
                if stype == OST.NUMBER:
                    stk.append(p[s])
                else:
                    pass  # TODO
        INSTRUCTIONS['='] = eq

        def gt(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == stype:
                stk.append(int(a > b))
            else:
                if stype == OST.NUMBER:
                    stk.append(OS.convert(p[s:], ptype))
                else:
                    pass  # TODO
        INSTRUCTIONS['>'] = gt

        def question(self, stk, prgm):
            a, b = stk.popn(2)
            p, s = OS.byprec([a, b])
            ptype, stype = map(OS.typeof, [p, s])
            if ptype == OST.ARRAY:
                if stype == OST.BLOCK:
                    for x in p:
                        stk.append(x)
                        prgm.run(s)
                        if stk.pop():
                            stk.append(x)
                            break
                else:
                    stk.push(p.index(s))
            elif ptype == OST.BLOCK:
                pass  # TODO
            elif ptype == OST.STRING:
                pass  # TODO
            elif ptype == OST.NUMBER:
                stk.append(a ** b)
        INSTRUCTIONS['?'] = question

        def roll(self, stk, prgm):
            count = stk.pop()
            xs = stk.popn(abs(count))
            if count < 0:
                stk.append(xs[-1])
                stk.extend(xs[:-1])
            else:
                stk.extend(xs[1:])
                stk.append(xs[0])
        INSTRUCTIONS['@'] = roll

        def leftbracket(self, stk, prgm):
            return OST.ARRAY
        INSTRUCTIONS['['] = leftbracket

        def swaptwo(self, stk, prgm):
            stk.extend([stk.pop(), stk.pop()])
        INSTRUCTIONS['\\'] = swaptwo

        def rightbracket(self, stk, prgm):
            return -OST.ARRAY
        INSTRUCTIONS[']'] = rightbracket

        def bitxor(self, stk, prgm):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable ^ enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append([x for x in a1 if x not in a2] +
                           [x for x in a2 if x not in a1])
            elif ptype == OST.BLOCK:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(block(''.join([c for c in s1 if c not in s2] +
                                         [c for c in s2 if c not in s1])))
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join([c for c in s1 if c not in s2] +
                                   [c for c in s2 if c not in s1]))
            elif ptype == OST.NUMBER:
                stk.append(a ^ b)
        INSTRUCTIONS['^'] = bitxor

        def backtick(self, stk, prgm):
            return OST.STRING
        INSTRUCTIONS['`'] = backtick

        def leftcurlybracket(self, stk, prgm):
            return OST.BLOCK
        INSTRUCTIONS['{'] = leftcurlybracket

        def bitor(self, stk, prgm):
            a, b = stk.popn(2)
            ptype = OS.typeof(OS.byprec([a, b])[0])

            # note: enumerable | enumerable does not use set() because
            # order must be guaranteed
            if ptype == OST.ARRAY:
                a1 = OS.convert(a, OST.ARRAY)
                a2 = OS.convert(b, OST.ARRAY)
                stk.append(uniq(a1 + a2))
            elif ptype == OST.BLOCK:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(block(''.join(uniq(s1 + s2))))
            elif ptype == OST.STRING:
                s1 = OS.tostr(a)
                s2 = OS.tostr(b)
                stk.append(''.join(uniq(s1 + s2)))
            elif ptype == OST.NUMBER:
                stk.append(a | b)
        INSTRUCTIONS['|'] = bitor

        # this normally isn't called unless there are unmatched brackets
        # block parsing is done within Ostrich#run
        def rightcurlybracket(self, stk, prgm):
            return -OST.BLOCK
        INSTRUCTIONS['}'] = rightcurlybracket

        def tilde(self, stk, prgm):
            x = stk.pop()
            xt = OS.typeof(x)
            if xt == OST.ARRAY:
                stk.extend(x)
            if xt == OST.BLOCK:
                prgm.run(x)
            if xt == OST.STRING:
                prgm.run(x)
            if xt == OST.NUMBER:
                stk.append(-x)
        INSTRUCTIONS['~'] = tilde

        return INSTRUCTIONS

    INSTRUCTIONS = initialize_instructions()

    def __init__(self):
        self.stack = OS()
        self.variables = defaultdict(lambda: None)
        self.state = None

    def run(self, code):
        self.state = None
        cumulstr = ''  # string, block
        nestcount = 1  # block
        markers = []   # array

        while code:

            instr = code[0]
            code = code[1:]

            if self.state == OST.STRING:
                if instr == '`':
                    self.stack.append(cumulstr)
                    cumulstr = ''
                    self.state = None
                else:
                    cumulstr += instr

            elif self.state == OST.BLOCK:
                if instr == '}':
                    nestcount -= 1
                    if nestcount == 0:
                        self.stack.append(block(cumulstr))
                        cumulstr = ''
                        nestcount = 1  # reset for next time
                        self.state = None
                    else:
                        cumulstr += instr
                else:
                    cumulstr += instr
                    if instr == '{':
                        nestcount += 1

            elif self.state == OS.XSTATE.ASSIGN:
                self.variables[instr] = self.stack[-1]
                self.state = None

            else:
                self.state = Ostrich.INSTRUCTIONS[instr](instr, self.stack, self)
                if self.state == OST.ARRAY:
                    markers.append(len(self.stack))
                elif self.state == -OST.ARRAY:
                    idx = markers.pop() if markers else 0
                    self.stack.append(self.stack.popn(-idx))
                elif type(self.state) is str and self.state.startswith(OS.XSTATE.RETRIEVE):
                    x = self.variables[self.state[len(OS.XSTATE.RETRIEVE):]]
                    if x:
                        if OS.typeof(x) == OST.BLOCK:
                            code = x + code
                        else:
                            self.stack.append(x)

        # finished parsing instr's
        # perform final cleanup

        if self.state == OST.STRING:
            self.stack.append(cumulstr)
        elif self.state == OST.BLOCK:
            self.stack.append(OS.convert(cumulstr, OST.BLOCK))
        self.state = None

        while markers:
            self.stack.append(self.stack.popn(-markers.pop()))

        return ' '.join(map(OS.inspect, self.stack))

# just for convenience
OS = Ostrich.Stack
OST = Ostrich.Stack.TYPES
block = Ostrich.Block

if __name__ == '__main__':
    import sys  # sys.exit, sys.stdin

    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', nargs='?',
        help='path to Ostrich file to execute, - for stdin'
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
        print('''This is Ostrich v%d.%d.%d%s
Type any command or \\\\help for help.''' % (
            Ostrich.MAJOR_VERSION,
            Ostrich.MINOR_VERSION,
            Ostrich.PATCH_VERSION,
            ' (%s)' % Ostrich.VERSION_DESC if Ostrich.VERSION_DESC else ''))
        # REPL
        import readline
        while True:
            # R
            try:
                code = input('>>> ')
            except (EOFError, KeyboardInterrupt):
                sys.exit('')
            # E
            if code[:2] == '\\\\':
                cmd = code[2:]
                if cmd == 'help':
                    rtn = 'Please see README.md. (this will give actual help soon)'
                else:
                    rtn = 'Unknown extended command `%s\'.' % cmd
            else:
                rtn = program.run(code)
            # P
            print(rtn)
            # L
    elif args.exec:
        # execute code!
        program.run(args.exec)
    elif args.filename:
        # resolve path, get code
        code = None
        if args.filename == '-':
            code = sys.stdin.read()
        else:
            import os
            path = os.path.abspath(args.filename)
            if not os.path.exists(path):
                sys.exit('Err: Path %s does not exist' % path)
            code = open(path).read()

        # execute code!
        program.run(code)
    else:
        parser.print_help()
