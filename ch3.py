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
    while True:
        save = idx
        # try to skip spaces
        while idx < len(s) and s[idx].isspace():
            idx += 1
        # try to skip a line comment
        if idx < len(s) and s[idx] ==';':
            idx += 1
            while idx < len(s) and s[idx] != '\n':
                idx += 1
        # no more spaces or comments
        if idx == save:
            break
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

def pl_eval(env, node):
    # read a vaiable
    if not isinstance(node, list):
        assert isinstance(node, str)
        return name_loopup(env, node)[node]
    # ...
    if node[0] in ('do', 'then', 'else') and len(node)>1:
        new_env = (dict(), env) # add the map as the linked list head
        for val in node[1:]:
            val = pl_eval(new_env, val)
        return val # the last item
    
    # ...
    # new variable
    if node[0] == 'var' and len(node) == 3:
        _, name, val = node
        scope, _ = env
        if name in scope:
            raise ValueError('duplicated name')
        val = pl_eval(env, val)
        scope[name] = val
        return val
    # update a variable
    if node[0] == 'set' and len(node) == 3:
        _, name, val = node
        scope = name_loopup(env, name)
        val = pl_eval(env, val)
        scope[name] = val
        return val

    # ...

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
        return op(pl_eval(env, node[1]), pl_eval(env, node[2]))
    
    # unary operators
    unops = {
        '-': operator.neg,
        'not': operator.not_,
    }
    if len(node) == 2 and node[0] in unops:
        op = unops[node[0]]
        return op(pl_eval(env, node[1]))
    
    # conditionals 
    if len(node) == 4 and node[0] == '?':
        _,cond, yes, no = node
        if pl_eval(env, cond):
            return pl_eval(env, yes)
        else:
            return pl_eval(env, no)
        
    # print
    if node[0] == 'print':
        return print(*(pl_eval(env, val) for val in node[1:]))
    
    raise ValueError('unknown expression')

def name_loopup(env, key):
    while env: # linked list traversal
        current, env = env
        if key in current:
            return current
    raise ValueError('undefined name')

def pl_parse_prog(s):
    return pl_parse('(do ' + s + ')')

def test_eval():
    def f(s):
        return pl_eval(None ,pl_parse_prog(s))
    
    # assert f('1') == 1
    # assert f('(+ 1 3)') == 4
    # assert f('(? (lt 1 3) "yes" "no")') == 'yes'
    # assert f('(print 1 2 3)') is None
#     assert f('''
#             ;; first scope
#              (var a 1)
#              (print a)
# ''') is None
    assert f('''
        ;; first scope
        (var a 1)
        (var b (+ a 1))
        ;; a=1, b=2
        (do
            ;; new scope
            (var a (+ b 5))     ;; name collision
            (set b (+ a 10))
        )
        ;; a=1, b=17
        (* a b)
    ''') == 17

test_eval()

# print (skip_space('    ts    et', 6))
# print (pl_eval(pl_parse('(? (lt 4 2) 3 2)')))

# print (pl_parse('(+ 3 5)'))
# print (pl_eval(pl_parse('(+ 3 5)')))