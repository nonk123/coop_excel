import re
import inspect

functions = {}

def evaluate_form(ctx, expression):
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

    fun = form[0]
    args = form[1:]

    args = [evaluate(ctx, arg) for arg in args]
    return cast(ctx, functions[fun](ctx, *args))

def evaluate(ctx, expression):
    if ctx["recursion"] > 100:
        raise RuntimeError("Recursion limit exceeded")

    ctx["recursion"] += 1

    fun = re.fullmatch(r"\((.*)\)", expression)

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

    return cell.get_value(ctx["recursion"])

def reduce(fun, *args):
    if not args:
        raise ValueError("Must supply arguments")

    x = args[0]

    for y in args[1:]:
        x = fun(x, y)

    return x

@lisp_fn("+")
def add(ctx, *operands):
    "Add numbers."
    return reduce(lambda x, y: x + y, *operands)

@lisp_fn("-")
def subtract(ctx, *operands):
    """Negate one number or subtract many."""

    if len(operands) == 1:
        return -operands[0]
    else:
        return reduce(lambda x, y: x - y, *operands)

@lisp_fn("*")
def multiply(ctx, *operands):
    "Multiply numbers."
    return reduce(lambda x, y: x * y, *operands)

@lisp_fn("/")
def divide(ctx, *operands):
    "Divide numbers."
    return reduce(lambda x, y: x / y, *operands)

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
