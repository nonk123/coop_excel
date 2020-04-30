import re

functions = {}

def evaluate(table, expression):
    form = re.fullmatch(r"\((?P<form>.*)\)", expression)

    if not form:
        return cast(expression)

    expression = form.group("form")

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

    if not form:
        return None

    fun = form[0]
    args = form[1:]

    if fun in functions:
        try:
            args = [evaluate(table, arg) for arg in args]
            return cast(functions[fun](table, *args))
        except:
            return None

    return None

def cast(expr):
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
def at(table, row, col):
    return table.get(int(row), int(col)).value

def reduce(fun, *args):
    if not args:
        return None

    x = args[0]

    for y in args[1:]:
        x = fun(x, y)

    return x

@lisp_fn("+")
def add(table, *args):
    return reduce(lambda x, y: x + y, *args)

@lisp_fn("-")
def subtract(table, *args):
    if len(args) == 1:
        return -args[0]
    else:
        return reduce(lambda x, y: x - y, *args)

@lisp_fn("*")
def multiply(table, *args):
    return reduce(lambda x, y: x * y, *args)

@lisp_fn("/")
def divide(table, *args):
    return reduce(lambda x, y: x / y, *args)
