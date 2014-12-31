# utility methods
def Enum(**enums): return type('Enum', (), enums)


class Stack(list):
    # all Ostrich types; also used for state management
    TYPES = Enum(NUMBER=0, STRING=1, BLOCK=2, ARRAY=3)
    # extra states (used for :, etc.)
    XSTATE = Enum(ASSIGN='_XASGN', EXIT='_XEXIT', CHAR='_XCHAR',
        CHARBLOCK = '_XCHBK')

    def typeof(x):
        xt = type(x)
        if xt is list:
            return OST.ARRAY
        if xt is block:
            return OST.BLOCK
        if xt is str:
            return OST.STRING
        if xt is int or xt is float:
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
                return ' '.join(map(lambda item: OS.convert(item, to_type), x))
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
            return ('%d' if type(x) is int else '%f') % x

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


# to differentiate blocks and strings
class Block(str): pass


# just for convenience
OS = Stack
OST = Stack.TYPES
block = Block
