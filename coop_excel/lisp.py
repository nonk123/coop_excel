import re

functions = {}

MAX_RECURSION = 100

def evaluate_form(ctx, expression):
    if ctx["recursion"] > MAX_RECURSION:
        return None

    form = [""]

    depth = 0

    for c in expression:
        if depth == 0 and c == " ":
            form.append("")
            continue

        if c == "(":
            depth += 1

        if c == ")":
            depth -= 1

        form[-1] += c

    form = [x.strip() for x in form if x.strip()]

    if not form:
        return None

    fun = form[0]
    args = form[1:]

    if fun in functions:
        try:
            args = [evaluate(ctx, arg) for arg in args]
            return cast(ctx, functions[fun](ctx, *args))
        except:
            return None

def evaluate(ctx, expression):
    fun = re.fullmatch(r"\((?P<form>.*)\)", expression)

    ctx["recursion"] += 1

    if fun:
        return evaluate_form(ctx, fun.group("form"))
    else:
        return cast(ctx, expression)

def cast(ctx, expr):
    if callable(expr):
        return expr

    expr = str(expr)

    string_match = re.fullmatch(r'(?<=\").*(?=\")', expr)

    if string_match:
        return string_match.group(0)

    try:
        return float(expr)
    except:
        return None

def lisp_fn(name=None):
    def decorator(fn):
        functions[name if name else fn.__name__] = fn
        return fn

    return decorator

@lisp_fn()
def at(ctx, row, col):
    return ctx["table"].get(int(row), int(col)).value

def reduce(fun, *args):
    if not args:
        return None

    x = args[0]

    for y in args[1:]:
        x = fun(x, y)

    return x

@lisp_fn("+")
def add(ctx, a, b, *rest):
    return reduce(lambda x, y: x + y, a, b, *rest)

@lisp_fn("-")
def subtract(ctx, a, *rest):
    if not rest:
        return -a
    else:
        return reduce(lambda x, y: x - y, a, *rest)

@lisp_fn("*")
def multiply(ctx, a, b, *rest):
    return reduce(lambda x, y: x * y, a, b, *rest)

@lisp_fn("/")
def divide(ctx, a, b, *rest):
    return reduce(lambda x, y: x / y, a, b, *rest)

@lisp_fn("1+")
def add_one(ctx, x):
    return x + 1

@lisp_fn("1-")
def subtract_one(ctx, x):
    return x - 1

@lisp_fn()
def row(ctx):
    return ctx["cell"].row

@lisp_fn()
def col(ctx):
    return ctx["cell"].col
