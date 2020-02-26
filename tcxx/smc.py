from pprint import pprint
from parser import parse_language, Op

language = [
        ('typeDef', '`type` n', lambda x: ('typeDef', x[0])),
        ('boxDef', '`box` n : T `->` T', lambda x: ('boxDef', x[0], (x[1], x[2]))),
        ('fDef', '`def` n = f', lambda x: ('def', x[0], x[1])),
        ('T', Op('|', 2, 'right'), lambda x, y: ('typePar', x, y)),
        ('T', 'n', lambda x: ('type', x[0])),
        ('f', '`and`', lambda x: ('and',)),
        ('f', '`or`',lambda x: ('or',)),
        ('f', Op('|', 2, 'right'), lambda x, y: ('par', x, y)),
        ('f', Op(';', 2, 'left'), lambda x, y: ('comp', x, y)),
        ('f', '(f)', lambda x: x),
        ('expr', 'fDef', lambda x: x[0]),
        ('expr', 'boxDef', lambda x: x[0]),
        ('expr', 'typeDef', lambda x: x[0]),
        ('expr', '`graph` f', lambda x: x[0]),
        ('L', '*expr', lambda x: x[0])
        ]

test = """
type A
box and : A|A -> A | A | A
box or : A | A -> A | A

def f = and | and

graph (and ; or) | or ; and
"""
#

pprint(parse_language(language, 'L', test, False))



