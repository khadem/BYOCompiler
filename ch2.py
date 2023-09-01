# Build your own compiler

def parse_expr(s:str, idx: int):
    idx = skip_space(s, idx)
    if s[idx] == '(':
        # a list
        idx += 1
        l = []
        while True:
            idx = skip_space(s, idx)
            if idx >= len(s):
                raise Exception('unbalanced parenthesis')
            if s[idx] == ')':
                idx += 1
                break

            idx, v = parse_expr(s, idx)
            l.append(v)
        return idx, l
    elif s[idx] == ')':
        raise Exception('bad parenthesis')
    else:
        # an atom
        start = idx
        while idx < len(s) and (not s[idx].isspace()) and s[idx] not in '()':
            idx += 1
        if start == idx:
            raise Exception('empty program')
        return idx, parse_atom(s[start:idx])

def skip_space(s, idx):
    while idx < len(s) and s[idx].isspace():
        idx += 1
    return idx

# bool, number, string or symbol
def parse_atom(s):
    # TODO: actually implement this
    import json
    try:
        return ['val', json.loads(s)]
    except json.JSONDecodeError:
        return s

def pl_parse(s):
    idx, node = parse_expr(s, 0)
    idx = skip_space(s, idx)
    if idx < len(s):
        raise ValueError('trailing garbage')
    return node

def pl_eval(node):
    if len(node) == 0:
        raise ValueError('empty list')
    
    # bool, number, string and etc
    if len(node) == 2 and node[0] == 'val':
        return node[1]
    
    # binary operator
    import operator
    binops = {
        '+': operator.add, 
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        'eq': operator.eq,
        'ne': operator.ne,
        'ge': operator.ge,
        'gt': operator.gt,
        'le': operator.le,
        'lt': operator.lt,
        'and': operator.and_,
        'or': operator.or_,
    }

    if len(node) == 3 and node[0] in binops:
        op = binops[node[0]]
        return op(pl_eval(node[1]), pl_eval(node[2]))
    
    # unary operators
    unops = {
        '-': operator.neg,
        'not': operator.not_,
    }
    if len(node) == 2 and node[0] in unops:
        op = unops[node[0]]
        return op(pl_eval(node[1]))
    
    # conditionals 
    if len(node) == 4 and node[0] == '?':
        _,cond, yes, no = node
        if pl_eval(cond):
            return pl_eval(yes)
        else:
            return pl_eval(no)
        
    # print
    if node[0] == 'print':
        return print(*(pl_eval(val) for val in node[1:]))
    
    raise ValueError('unknown expression')


def test_eval():
    def f(s):
        return pl_eval(pl_parse(s))
    
    assert f('1') == 1
    assert f('(+ 1 3)') == 4
    assert f('(? (lt 1 3) "yes" "no")') == 'yes'
    assert f('(print 1 2 3)') is None


test_eval()

# print (skip_space('    ts    et', 6))
# print (pl_eval(pl_parse('(? (lt 4 2) 3 2)')))

# print (pl_parse('(+ 3 5)'))
# print (pl_eval(pl_parse('(+ 3 5)')))