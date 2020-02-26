
from functools import namedtuple
from pprint import pprint

class ParseError(BaseException): pass

def recursive_descent_matcher(rules, start, index, tokens, debug=False):
    def iseof(tokens, idx):
        try:
            x = tokens[idx]
            return False
        except IndexError: return True

    longest_match = [0]
    def advance(i): longest_match[0] = max(longest_match[0],i)

    dpth = [0]
    def sp(i): return '  '.join(['' for x in range(i)])

    def parse(rule, idx):
        dpth[0] += 1
        rs = [ (r,p,a) for r, p, a in rules if r == rule]
        for r,p,a in rs:
            if debug: print(sp(dpth[0]) + "⇒'%s' : %s : %s..." % (r, str(p), tokens[idx:idx+10]))
            i = idx
            match = []
            matched = True
            for x in p:
                if isinstance(x, str): # recursive or eof
                    if x == '⊣':
                        if not iseof(tokens, i):
                            matched = False
                            break
                    else:
                        res = parse(x, i)
                        if res is None:
                            matched = False
                            break
                        (res, j) = res
                        match.append(res)
                        i = j
                else: # terminal
                    if iseof(tokens, i):
                        matched = False
                        break
                    if x(tokens[i]):
                        match.append(tokens[i])
                        i += 1
                    else:
                        matched = False
                        break
            if debug:
                if matched: print(sp(dpth[0]) + "✓'%s' : '%s ...'" % (r, tokens[i:i+10]))
                else: print(sp(dpth[0]) + "✗'%s' : '%s ...'" % (r, tokens[idx:idx+10]))
            if matched:
                advance(i)
                dpth[0] -= 1
                return (a(match), i)
        dpth[0] -= 1
        return None
    res = parse(start,index)
    if res == None:
        lm = longest_match[0]
        l,c = posToLineCol(lm, tokens)
        raise ParseError('Parse error: %d:%d: ... "%s" ...)' % (l,c, tokens[lm:lm+10]))
        # raise ParseError('Parse error at pos %d: ... "%s" ...)' % (lm, tokens[lm:lm+10]))
    return res


def posToLineCol(pos, s):
    l = 1
    c = 1
    for i in range(pos):
        if s[i] == '\n':
            l += 1
            c = 1
        else:
            c += 1
    return l,c


class ischr:
    def __init__(self, c): self.c = c
    def __call__(self, t): return self.c == t
    def __str__(self): return self.c
    def __repr__(self): return "ischr('%s')" % self.c

# def ischr(c): return lambda t: t == c

def plus_star_rule(rule, collect=True):
    rule_star = rule + '*'
    rule_plus = rule + '+'
    if collect:
        cons = lambda x, y: [x] + y
        nil = []
    else:
        cons = lambda x, y: None
        nil = None
    rules = [
        (rule_star, [rule, rule_star], lambda x: cons(x[0], x[1])),
        (rule_star, [], lambda x: nil),
        (rule_plus, [rule, rule_star], lambda x: cons(x[0], x[1]))
    ]
    return rules


def unaryop_rules(name, op_char, constr):
    return [
        (name, [ischr(op_char), ' *', name], lambda x: constr(x[2])),
    ]

def binop_rules(name, op_char, tighter_expr, assoc, constr):
    name_rest = name + '₂'
    name_rest_star = name_rest + '*'
    def rred(l):
        head = l[0]
        tail = l[1:]
        if tail == []: return head
        return constr(head, rred(tail))

    def lred(l):
        last = l[-1]
        front = l[:-1]
        if front == []: return last
        return constr(lred(front), last)

    if assoc == 'left':
        red = lred
    else:
        red = rred

    rules = [
        (name, [tighter_expr, name_rest_star], lambda x: red([x[0]] + x[1])),
        (name_rest, [' *'] + [ ischr(c) for c in op_char] + [' *', tighter_expr], lambda x: x[2 + len(op_char)])
    ]
    rules += plus_star_rule(name_rest)
    return rules

def notation_to_rules(name, format, f):
    additional_rules = []
    rule = []
    s = format
    i = 0
    idx = []
    while i < len(s):
        if s[i].isalpha():
            sym = ''
            while i < len(s) and s[i].isalpha():
                sym += s[i]
                i += 1
            rule.append(sym)
            idx.append(len(rule)-1)
        elif s[i] in ('*', '+'):
            it = s[i]
            sym = ''
            i += 1
            while i < len(s) and s[i].isalpha():
                sym += s[i]
                i += 1
            additional_rules += plus_star_rule(sym, collect=True)
            rule.append(sym + it)
            idx.append(len(rule)-1)
        elif s[i] == '`':
            i += 1
            while i < len(s):
                if s[i] == '`': break
                rule.append(ischr(s[i]))
                i += 1
            i += 1
        elif s[i] == ' ':
            i += 1
            continue
        else:
            rule.append(ischr(s[i]))
            i += 1
        if i < len(s): rule.append(' *')
    return additional_rules + [(name, rule, lambda x: f([x[i] for i in idx]))]


Op = namedtuple('Op', ['symbol', 'arity', 'assoc']);

def gen_grammar_rules(language):
    rules = [
        (' ', [lambda t: t.isspace()], lambda x: None),
        ('char', [lambda t: t.isalpha()], lambda x: x[0]),
        ('digit', [lambda t: t.isnumeric()], lambda x: x[0]),
    ]
    rules += plus_star_rule(' ', collect=False)
    rules += plus_star_rule('char', collect=True)
    rules += plus_star_rule('digit', collect=True)

    rules += [
        ('n', ['char+', 'digit*'], lambda x: ''.join(x[0] + x[1])),
        ('num', ['digit+'], lambda x: int(''.join(x[0])))
    ]

    syntax_categories = set([x[0] for x in language])

    for syn in syntax_categories:
        level = 0
        syn_lang = [ x for x in language if x[0] == syn ]
        notations = [ x[1:] for x in syn_lang if isinstance(x[1], str) ]
        opreations = [ [x[1].symbol, x[1].arity, x[1].assoc, x[2]] for x in syn_lang if isinstance(x[1], Op) ]

        rules += [
            (syn + '0', [ischr('('), ' *', syn, ' *', ischr(')')], lambda x: x[2]),
        ]

        for char, arity, assoc, template in opreations:
            synlevel = syn + str(level)
            synnextlevel = syn + str(level+1)
            if arity == 2:
                rules += binop_rules(synnextlevel, char, synlevel, assoc, template)
                level +=1
            elif arity == 1:
                rules += unaryop_rules(syn + '0', char, template)

        for format, template in notations:
            rules += notation_to_rules(syn + '0', format, template)

        rules += [
            (syn, [syn + str(level)], lambda x: x[0]),
            (syn, [' +', syn], lambda x: x[1]),
        ]

    return rules

def parse_language(language, syn_cat, source, debug=False):
    rules = gen_grammar_rules(language)
    if debug:
        pprint(rules)
    r = rules + [('START', [syn_cat, ' *', '⊣'], lambda x: x[0])]
    return recursive_descent_matcher(r, 'START', 0, source, debug=debug)


