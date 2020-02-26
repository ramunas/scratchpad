from parser import Op, parse_language
from pprint import pprint

language = [
        ('a', 'n(n)', lambda x: ('inp',x[0],x[1])),
        ('a', 'n<n>', lambda x: ('out',x[0],x[1])),
        ('s', 'a.p', lambda x: ('prefix', x[0], x[1])),
        ('s', Op('+', 2, 'right'), lambda x, y: ('sum', x, y)),
        ('p', 's', lambda x: x[0]),
        ('p', '0', lambda x: ('0',)),
        ('p', 'a.p', lambda x: ('prefix', x[0], x[1])),
        ('p', '(`new` n)p', lambda x: ('new', x[0], x[1])),
        ('p', '(q)', lambda x: x[0]),
        ('q', Op('|', 2, 'right'), lambda x, y: ('pll', x, y)),
        ('q', 'p', lambda x: x[0])
        ]

pptable = [
        ('inp', '0(1)'),
        ('out', '0<1>'),
        ('prefix', '0.1'),
        ('sum', '(0 + 1)'),
        ('0', '\\0'),
        ('pll', '(0 | 1)'),
        ('new', '(new 0)1')
        ]

def parse(inp):
    return parse_language(language, 'q', inp, False)[0]

def pp(x):
    s = ''
    if isinstance(x, tuple):
        for cons, fmt in pptable:
            if x[0] == cons:
                args = x[1:]
                escape = False
                for f in fmt:
                    if escape:
                        s += f
                        escape = False
                    elif f == '\\':
                        escape = True
                    elif f in '0123456789':
                        s += pp(args[int(f)])
                    else:
                        s += f
    else:
        s = x
    return s



test = """

a(b).0 + x(b).(x<x>.0+x<x>.0) + y<y>.0 + w<w>.0 + u<w>.0 |
(new n)n<n>.(0 | 0) |
u<w>.0 |
x<x>.0

"""

test2 = """
n<x>.0
"""

pprint(parse(test))
print(test)
print(pp(parse(test)))
print(pp(parse(pp(parse(test)))))
print(pp(parse(test)) == pp(parse(pp(parse(test)))))


