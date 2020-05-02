import re
import inspect

functions = {}

def evaluate_form(ctx, expression, visited):
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
            args = [evaluate(ctx, arg, visited) for arg in args]
            return cast(ctx, functions[fun](ctx, *args))
        except:
            return None

def detect_cycle(v, l):
    occurences = {}

    for i, p in enumerate(l):
        if p == v and l[i] != p:
            occurences.setdefault(p, 0)
            occurences[p] += 1

    if v in occurences and occurences[v] > 1:
        return True

    l.append(v)

    return False

def evaluate(ctx, expression, visited=[]):
    if detect_cycle((row(ctx), col(ctx)), visited):
        return None

    fun = re.fullmatch(r"\((.*)\)", expression)

    if fun:
        ret = evaluate_form(ctx, fun.group(1), visited)
    else:
        ret = cast(ctx, expression)

    return ret

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

        fn.lisp_args = []

        for name, param in inspect.signature(fn).parameters.items():
            name = name.upper()

            if param.kind == param.VAR_KEYWORD:
                fn.lisp_args.append(f"&key {name}")
            elif param.kind == param.VAR_POSITIONAL:
                fn.lisp_args.append(f"&rest {name}")
            else:
                fn.lisp_args.append(name)

            if param.default != param.empty:
                fn.lisp_args[-1] += f"={param.default}"

        fn.lisp_args = fn.lisp_args[1:]

        for alias in names[1:]:
            def aliased(*args, **kwargs):
                return fn(*args, **kwargs)

            aliased.__name__ = alias
            aliased.__doc__ = f"""Alias for `{real_name}'."""
            aliased.lisp_args = fn.lisp_args

            functions[alias] = aliased

        return fn

    return decorator

@lisp_fn("at", "$")
def at(ctx, row, col):
    """Get the cell's value at ROW and COL."""
    cell = ctx["table"].get(int(row), int(col))

    if ctx["cell"] not in cell.dependants:
        cell.dependants.append(ctx["cell"])

    return cell.value

def reduce(fun, *args):
    if not args:
        return None

    x = args[0]

    for y in args[1:]:
        x = fun(x, y)

    return x

@lisp_fn("+")
def add(ctx, a, b, *etc):
    """Add two or more numbers."""
    return reduce(lambda x, y: x + y, a, b, *etc)

@lisp_fn("-")
def subtract(ctx, a, *etc):
    """Subtract two or more numbers. Negate A if it is the only parameter."""

    if not etc:
        return -a
    else:
        return reduce(lambda x, y: x - y, a, *etc)

@lisp_fn("*")
def multiply(ctx, a, b, *etc):
    """Multiply two or more numbers."""
    return reduce(lambda x, y: x * y, a, b, *etc)

@lisp_fn("/")
def divide(ctx, a, b, *etc):
    """Divide two or more numbers."""
    return reduce(lambda x, y: x / y, a, b, *etc)

@lisp_fn("1+")
def add_one(ctx, x):
    """Same as (+ X 1)"""
    return x + 1

@lisp_fn("1-")
def subtract_one(ctx, x):
    """Same as (- X 1)"""
    return x - 1

@lisp_fn("above", "^")
def above(ctx, n=1):
    """Get the cell N above the current."""
    return at(ctx, row(ctx) - n, col(ctx))

@lisp_fn("below", "v")
def below(ctx, n=1):
    """Get the cell N below the current."""
    return at(ctx, row(ctx) + n, col(ctx))

@lisp_fn()
def row(ctx):
    """Get this cell's row."""
    return ctx["cell"].row

@lisp_fn()
def col(ctx):
    """Get this cell's column."""
    return ctx["cell"].col
