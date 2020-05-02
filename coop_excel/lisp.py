import re
import inspect

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
    fun = re.fullmatch(r"\((.*)\)", expression)

    ctx["recursion"] += 1

    if fun:
        return evaluate_form(ctx, fun.group(1))
    else:
        return cast(ctx, expression)

def cast(ctx, expr):
    try:
        return float(expr)
    except:
        return expr

def lisp_fn(*args):
    def decorator(fn):
        names = args if args else [fn.__name__]

        real_name = names[0]

        functions[real_name] = fn

        fn.lisp_args = inspect.signature(fn).parameters.keys()

        for alias in names[1:]:
            def aliased(*args, **kwargs):
                return fn(*args, **kwargs)

            aliased.__name__ = alias
            aliased.__doc__ = f"""Alias for function `{real_name}'."""
            aliased.lisp_args = fn.lisp_args

            functions[alias] = aliased

        return fn

    return decorator

@lisp_fn("at", "$")
def at(ctx, row, col):
    """Get the cell's value at ROW and COL."""
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
    """Add two or more numbers."""
    return reduce(lambda x, y: x + y, a, b, *rest)

@lisp_fn("-")
def subtract(ctx, a, *rest):
    """Subtract two or more numbers. Negate A if it is the only parameter."""

    if not rest:
        return -a
    else:
        return reduce(lambda x, y: x - y, a, *rest)

@lisp_fn("*")
def multiply(ctx, a, b, *rest):
    """Multiply two or more numbers."""
    return reduce(lambda x, y: x * y, a, b, *rest)

@lisp_fn("/")
def divide(ctx, a, b, *rest):
    """Divide two or more numbers."""
    return reduce(lambda x, y: x / y, a, b, *rest)

@lisp_fn("1+")
def add_one(ctx, x):
    """Same as (+ X 1)"""
    return x + 1

@lisp_fn("1-")
def subtract_one(ctx, x):
    """Same as (- X 1)"""
    return x - 1

@lisp_fn()
def row(ctx):
    """Get this cell's row."""
    return ctx["cell"].row

@lisp_fn()
def col(ctx):
    """Get this cell's column."""
    return ctx["cell"].col
