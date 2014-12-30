#!/usr/bin/env python3

from collections import defaultdict
import itertools
import sys  # sys.exit, sys.stdin, sys.stdout

# Ostrich internal libs
import ost_instructions, ost_repl, ost_stack


# utility methods
def uniq(s):
    # http://stackoverflow.com/q/480214/1223693
    seen = set()
    return [x for x in s if x not in seen and not seen.add(x)]


class Ostrich:
    MAJOR_VERSION = 0
    MINOR_VERSION = 3
    PATCH_VERSION = 1
    # VERSION_DESC = None
    VERSION_DESC = 'alpha'

    def __init__(self):
        self.stack = OS()
        self.variables = defaultdict(lambda: None)
        self.state = None

    def run(self, code):
        self.state = None
        cumulstr = ''  # string, block
        nestcount = 1  # block
        markers = []   # array
        INSTRUCTIONS = ost_instructions.ost_instructions()

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
                var = self.variables[instr]
                if var:
                    if OS.typeof(var) == OST.BLOCK:
                        code = var + code
                    else:
                        self.stack.append(var)
                else:
                    self.state = INSTRUCTIONS[instr](instr, self.stack, self)
                    if self.state == OST.ARRAY:
                        markers.append(len(self.stack))
                    elif self.state == -OST.ARRAY:
                        idx = markers.pop() if markers else 0
                        self.stack.append(self.stack.popn(-idx))
                    elif self.state == OS.XSTATE.EXIT:
                        code = ''

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
OS = ost_stack.Stack
OST = ost_stack.Stack.TYPES
block = ost_stack.Block

if __name__ == '__main__':
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
        '-e', '--execute', help='execute a string passed as an argument'
    )
    parser.add_argument(
        '-v', '--version', action='store_true',
        help='get the version of Ostrich that is being run'
    )

    args = parser.parse_args()
    program = Ostrich()
    version_string = 'Ostrich v%d.%d.%d%s' % (
        Ostrich.MAJOR_VERSION,
        Ostrich.MINOR_VERSION,
        Ostrich.PATCH_VERSION,
        ' (%s)' % Ostrich.VERSION_DESC if Ostrich.VERSION_DESC else ''
    )
    if args.interactive:
        print('''This is %s
Type any command or \\\\help for help.''' % version_string)
        ost_repl.ost_repl(program)
    elif args.version:
        print(version_string)
    elif args.execute:
        # execute code!
        program.run(args.execute)
        for x in program.stack:
            sys.stdout.write(OS.tostr(x))
    elif args.filename:
        # resolve path, get code
        code = None
        if args.filename == '-':
            code = sys.stdin.read()
        else:
            import os
            path = os.path.abspath(args.filename)
            if not os.path.exists(path):
                sys.exit('Ostrich: Path %s does not exist' % path)
            code = open(path).read()

        # execute code!
        program.run(code)
        for x in program.stack:
            sys.stdout.write(OS.tostr(x))
    else:
        parser.print_help()
