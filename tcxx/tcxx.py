
from functools import namedtuple
from pprint import pprint

from parser import parse_language, Op


language = [
        ('Defs', '*Def', lambda x: x),
        ('Def', 'n(n *ns) { e }', lambda x: [x[0], [x[1]] + x[2], x[3] ]),
        ('ns', ', n', lambda x: x[0]),
        ('e', 'n(e)', lambda x: x),
        ('e', '`for` (e;e;e) { e } e', lambda x: x),
        ('e', 'c', lambda x: x[0]),
        ('e', 'T n = e; e', lambda x: x),
        ('e', Op('*', 2, 'right'), lambda x, y: [x,y]),
        ('e', Op('/', 2, 'right'), lambda x, y: [x,y]),
        ('e', Op('+', 2, 'right'), lambda x, y: [x,y]),
        ('e', Op('-', 2, 'right'), lambda x, y: [x,y]),
        ('e', Op('<<', 2, 'right'), lambda x, y: [x,y]),
        ('e', Op('>>', 2, 'right'), lambda x, y: [x,y]),
        ('e', 'n', lambda x: x[0]),
        ('c', 'num', lambda x: x[0]),
        ('T', '`int`', lambda x: x)
        ]

test = """
hello(a1, b, c)
{
    int x = 10;
    int y = (20 + x * 2) >> 1234;
    for (1; 2; 3) {
        2 + 2
    }

    other(a1+42 + 3 + 6 + 10)
}

another(ddef, three) {
    int var = 2;
    1
}
another(ddef, three) {
    int var = 2;
    1
}

"""

test2 = """
term zero;
term succ(x);

term add(x,y);

rule add(zero, succ(x)) -> zero;
rule add(succ(x), y) -> add(x, succ(y));
"""

pprint(parse_language(language, 'Defs', test, False))


