import math
from collections import defaultdict
from copy import deepcopy

# ------------------ Tokenizer ------------------
def tokenize(s):
    tokens, num = [], ""
    for ch in s:
        if ch.isdigit():
            num += ch
        else:
            if num:
                tokens.append(int(num))
                num = ""
            if ch.strip():
                tokens.append(ch)
    if num:
        tokens.append(int(num))
    return tokens

# ------------------ AST ------------------
class AST:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# ------------------ Parser ------------------
def parse(tokens):
    def factor(i):
        if isinstance(tokens[i], int):
            return AST(tokens[i]), i+1
        if tokens[i] == '(':
            node, j = expr(i+1)
            return node, j+1
        raise ValueError

    def term(i):
        node, i = factor(i)
        while i < len(tokens) and tokens[i] in ('*','/'):
            op = tokens[i]
            right, i = factor(i+1)
            node = AST(op, node, right)
        return node, i

    def expr(i):
        node, i = term(i)
        while i < len(tokens) and tokens[i] in ('+','-'):
            op = tokens[i]
            right, i = term(i+1)
            node = AST(op, node, right)
        return node, i

    node, _ = expr(0)
    return node

# ------------------ Dual Numbers (Auto Diff) ------------------
class Dual:
    def __init__(self, val, der=0):
        self.val = val
        self.der = der

    def __add__(self, other):
        return Dual(self.val + other.val, self.der + other.der)

    def __sub__(self, other):
        return Dual(self.val - other.val, self.der - other.der)

    def __mul__(self, other):
        return Dual(self.val*other.val, self.val*other.der + self.der*other.val)

    def __truediv__(self, other):
        return Dual(self.val/other.val,
                    (self.der*other.val - self.val*other.der)/(other.val**2))

# ------------------ AST Evaluation ------------------
def eval_ast(node, x=None):
    if isinstance(node.val, int):
        return Dual(node.val, 0) if x else node.val
    a = eval_ast(node.left, x)
    b = eval_ast(node.right, x)

    if node.val == '+': return a + b
    if node.val == '-': return a - b
    if node.val == '*': return a * b
    if node.val == '/': return a / b

# ------------------ Polynomial Algebra ------------------
def poly_add(a, b):
    res = defaultdict(int)
    for k,v in a.items(): res[k] += v
    for k,v in b.items(): res[k] += v
    return dict(res)

def poly_mul(a, b):
    res = defaultdict(int)
    for i,v in a.items():
        for j,w in b.items():
            res[i+j] += v*w
    return dict(res)

# ------------------ Gaussian Elimination ------------------
def gauss(A, b):
    n = len(A)
    for i in range(n):
        pivot = i
        for j in range(i+1, n):
            if abs(A[j][i]) > abs(A[pivot][i]):
                pivot = j
        A[i], A[pivot] = A[pivot], A[i]
        b[i], b[pivot] = b[pivot], b[i]

        for j in range(i+1, n):
            if A[i][i] == 0: continue
            ratio = A[j][i] / A[i][i]
            for k in range(i, n):
                A[j][k] -= ratio * A[i][k]
            b[j] -= ratio * b[i]

    x = [0]*n
    for i in reversed(range(n)):
        s = sum(A[i][j]*x[j] for j in range(i+1, n))
        x[i] = (b[i] - s) / (A[i][i] if A[i][i] else 1)
    return x

# ------------------ Persistent Segment Tree ------------------
class PST:
    def __init__(self, l, r, val=0, left=None, right=None):
        self.l, self.r = l, r
        self.val = val
        self.left = left
        self.right = right

def pst_build(arr, l, r):
    if l == r:
        return PST(l, r, arr[l])
    m = (l+r)//2
    left = pst_build(arr,l,m)
    right = pst_build(arr,m+1,r)
    return PST(l,r,left.val+right.val,left,right)

def pst_update(node, idx, val):
    if node.l == node.r:
        return PST(node.l,node.r,val)
    m = (node.l+node.r)//2
    if idx <= m:
        left = pst_update(node.left, idx, val)
        return PST(node.l,node.r,left.val+node.right.val,left,node.right)
    else:
        right = pst_update(node.right, idx, val)
        return PST(node.l,node.r,node.left.val+right.val,node.left,right)

def pst_query(node, l, r):
    if r < node.l or node.r < l:
        return 0
    if l <= node.l and node.r <= r:
        return node.val
    return pst_query(node.left,l,r) + pst_query(node.right,l,r)

# ------------------ Constraint Solver ------------------
def solve_constraints(vars, constraints):
    def backtrack(assign):
        if len(assign) == len(vars):
            return assign
        v = vars[len(assign)]
        for val in range(1,5):
            assign[v] = val
            if all(c(assign) for c in constraints):
                res = backtrack(assign)
                if res:
                    return res
            del assign[v]
        return None
    return backtrack({})

# ------------------ Minimax (Game Search) ------------------
def minimax(depth, maximizing, alpha, beta):
    if depth == 0:
        return math.sin(depth*3+1)

    if maximizing:
        best = -1e9
        for i in range(3):
            val = minimax(depth-1, False, alpha, beta)
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = 1e9
        for i in range(3):
            val = minimax(depth-1, True, alpha, beta)
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

# ------------------ Pipeline ------------------
def main():
    # Expression + autodiff
    expr = "(2+3)*(4+5)"
    ast = parse(tokenize(expr))
    val = eval_ast(ast)
    dval = eval_ast(ast, x=True).der

    # Polynomial
    p1 = {0:1,1:2}
    p2 = {0:3,2:1}
    poly = poly_mul(p1,p2)

    # Linear system
    A = [[2,1],[5,7]]
    b = [11,13]
    sol = gauss(A,b)

    # Persistent segment tree
    arr = [1,2,3,4]
    root = pst_build(arr,0,3)
    root2 = pst_update(root,2,10)
    seg_sum = pst_query(root2,0,3)

    # Constraint solving
    vars = ['a','b','c']
    constraints = [
        lambda d: 'a' not in d or d['a'] != 2,
        lambda d: 'b' not in d or d['b'] > 1,
        lambda d: len(d)<3 or d['a']+d['b']!=d['c']
    ]
    cs = solve_constraints(vars,constraints)

    # Game search
    game = minimax(5, True, -1e9, 1e9)

    return int(val + dval + sum(poly.values()) + sum(sol) + seg_sum + sum(cs.values()) + game)

if __name__ == "__main__":
    print(main())
