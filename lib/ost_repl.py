import readline  # better input()
import sys       # sys.exit()
from collections import defaultdict


repl_settings = {
    'autoclear': False,
    'prompt': '>>>'
}

def ost_repl(program):
    while True:
        # R
        try:
            code = input(repl_settings['prompt'] + ' ')
        except (EOFError, KeyboardInterrupt):
            sys.exit('')
        # E
        if code[:2] == '\\\\':
            cmd = code[2:]
            name, *args = cmd.split()
            rtn = COMMANDS[name](' '.join(args))
        else:
            rtn = program.run(code)
        # P
        print(rtn)
        # L
        if repl_settings['autoclear']:
            program.stack = []

def unknowncmd():
    def unknowncmd_inner(args):
        '''Unknown extended command.'''
        return 'Unknown extended command.'
    return unknowncmd_inner
COMMANDS = defaultdict(unknowncmd)

def _help(cmdname):
    '''Provides help on how to use Ostrich and this REPL.'''
    if cmdname:
        return COMMANDS[cmdname].__doc__
    else:
        return 'Please see README.md for general information about Ostrich, type \
\\\\commands for a list of all extended commands, or type \\\\help COMMANDNAME \
for help on a specific command.'
COMMANDS['help'] = _help

def commands(args):
    '''Shows a list of all extended commands.'''
    return 'List of extended commands: %s' % ', '.join(COMMANDS.keys())
COMMANDS['commands'] = commands

def autoclear(args):
    '''Whether to automatically clear the stack after every command is typed \
or not.'''
    if args:
        if args == 'on':
            repl_settings['autoclear'] = True
            return 'Autoclear enabled.'
        elif args == 'off':
            repl_settings['autoclear'] = False
            return 'Autoclear disabled.'
        else:
            return 'Please type either \\\\autoclear on or \\\\autoclear off \
to enable or disable autoclear.'
    else:
        return 'Autoclear is currently %s. To change this setting, type \
\\\\autoclear [on/off].' % \
            ['disabled', 'enabled'][int(repl_settings['autoclear'])]
COMMANDS['autoclear'] = autoclear

def prompt(args):
    '''The prompt shown when requesting user input on the REPL.'''
    if args:
        repl_settings['prompt'] = args
        return 'Prompt set to `%s\'.' % args
    else:
        return 'The prompt is currently `%s\'. To change it, type \\\\prompt \
[PROMPT].' % repl_settings['prompt']
COMMANDS['prompt'] = prompt
