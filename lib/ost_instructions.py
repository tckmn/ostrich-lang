from collections import defaultdict
import random

import ost_stack


def ost_instructions():
    def unknowninstr():
        def unknowninstr_inner(self, stk, prgm):
            pass
        return unknowninstr_inner
    INSTRUCTIONS = defaultdict(unknowninstr)

    # TODO things not in GS: A-Za-z_

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

    def arrset(self, stk, prgm):
        arr, idx, val = stk.popn(3)
        atype = OS.typeof(arr)
        if idx >= len(arr):
            arr += (' ' if atype == OST.STRING else [0]) * (idx - len(arr) + 1)
        val = OS.convert(val, atype)
        arr = arr[:idx] + val + arr[idx+1:]
        stk.append(arr)
    INSTRUCTIONS['#'] = arrset

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
                pass  # TODO block%number
            elif stype == OST.STRING:
                marker = len(stk)
                for x in s:
                    prgm.run(OS.inspect(x))
                    prgm.run(p)
                stk.append(stk[marker:])
                del stk[marker:-1]
            else:
                pass  # TODO block%block
        elif ptype == OST.STRING:
            if stype == OST.NUMBER:
                stk.append(p[::s])
            else:
                split = list(a) if b == '' else a.split(b)
                stk.append(list(filter(None, split)))
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
            prgm.run(x)
            while stk.pop(): prgm.run(x)
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
            prgm.run(x)
            while not stk.pop(): prgm.run(x)
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
                stk.append(s.join(map(OS.tostr, p)))
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
            stk.append([p[i:i+s] for i in range(0, len(p), s)])
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
                try:
                    stk.append(p.index(s))
                except ValueError:
                    stk.append(-1)
        elif ptype == OST.BLOCK:
            pass  # TODO
        elif ptype == OST.STRING:
            try:
                stk.append(p.index(OS.tostr(s)))
            except ValueError:
                stk.append(-1)
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

    def letter_B(self, stk, prgm):
        a, b = stk.popn(2)
        at = OS.typeof(a)
        if at == OST.ARRAY:
            num = 0
            for d in a:
                num *= b
                num += d
            stk.append(num)
        elif at == OST.NUMBER:
            arr = []
            while a:
                a, val = divmod(a, b)
                arr.append(val)
            stk.append(list(reversed(arr)))
    INSTRUCTIONS['B'] = letter_B

    def letter_E(self, stk, prgm):
        return OS.XSTATE.EXIT
    INSTRUCTIONS['E'] = letter_E

    def letter_G(self, stk, prgm):
        stk.append(sys.stdin.read())
    INSTRUCTIONS['G'] = letter_G

    def letter_I(self, stk, prgm):
        a, b, c = stk.popn(3)
        toRun = b if c else a
        if OS.typeof(toRun) == OST.BLOCK:
            prgm.run(toRun)
        else:
            stk.append(toRun)
    INSTRUCTIONS['I'] = letter_I

    def letter_P(self, stk, prgm):
        sys.stdout.write(OS.tostr(stk.pop()))
    INSTRUCTIONS['P'] = letter_P

    def letter_R(self, stk, prgm):
        stk.append(random.random())
    INSTRUCTIONS['R'] = letter_R

    def letter_Z(self, stk, prgm):
        l = stk.pop()
        allStr = all(OS.typeof(x) == OST.STRING for x in l)

        transposed = zip(*l)
        if allStr:
            transposed = map(''.join, transposed)
        else:
            transposed = map(list, transposed)

        stk.append(list(transposed))
    INSTRUCTIONS['Z'] = letter_Z

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

# just for convenience
OS = ost_stack.Stack
OST = ost_stack.Stack.TYPES
block = ost_stack.Block
