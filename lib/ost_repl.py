import readline  # better input()
import sys       # sys.exit()


def ost_repl(program):
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
                rtn = '''Please see README.md for general information about
Ostrich, type \\\\commands for a list of all extended commands, or type
\\\\help COMMANDNAME for help on a specific command.'''
            else:
                rtn = 'Unknown extended command `%s\'.' % cmd
        else:
            rtn = program.run(code)
        # P
        print(rtn)
        # L
