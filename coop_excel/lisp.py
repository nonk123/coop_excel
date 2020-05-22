import re
import inspect

RECURSION_LIMIT = 100

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
    if ctx["recursion"] > RECURSION_LIMIT:
        raise RuntimeError("Recursion limit exceeded")

    ctx["recursion"] += 1

    function = re.fullmatch(r"\((.*)\)", expression)

    if function:
        return evaluate_form(ctx, function.group(1))
    else:
        return cast(ctx, expression)

def cast(ctx, expr):
    if not isinstance(expr, str):
        return expr

    expr = expr

    if re.fullmatch(r"\d+", expr):
        return int(expr)
    elif re.fullmatch(r"\d+\.\d+|\d+\.|\.\d+", expr):
        return float(expr)
    else:
        return expr

def alias(name, real):
    def aliased(*args, **kwargs):
        return real(*args, **kwargs)

    aliased.__name__ = name
    aliased.__doc__ = f"Alias for `{real.__name__}'."

    return aliased

def defun(*aliases):
    def decorator(fn):
        names = aliases if aliases else [fn.__name__]

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

        for name in names[1:]:
            aliased = alias(name, fn)
            aliased.lisp_args = fn.lisp_args
            functions[name] = aliased

        return fn

    return decorator

def flatten(sequence):
    flat = []

    for element in sequence:
        if isinstance(element, list):
            flat += flatten(element)
        elif isinstance(element, CellRange):
            flat += flatten(elt["value"] for elt in element)
        else:
            flat.append(element)

    return flat

@defun("at", "$")
def at(ctx, row, col):
    """Get the cell's value at ROW and COL."""
    cell = ctx["table"].get(int(row), int(col))

    if ctx["cell"] not in cell.dependants:
        cell.dependants.append(ctx["cell"])

    return cell.get_value(ctx["recursion"])

def reduce(_type, fun, *args):
    if not args:
        raise ValueError("Must supply arguments")

    args = flatten(args)

    def check(x):
        if isinstance(x, _type):
            return x
        elif isinstance(x, dict):
            return check(x["value"])

        try:
            return _type(x)
        except:
            raise TypeError(f"Expected {str(_type)}, got {str(type(x))}")

    x = check(args[0])

    for y in args[1:]:
        x = fun(check(x), check(y))

    return x

@defun("+")
def add(ctx, *operands):
    "Add numbers."
    return reduce(float, lambda x, y: x + y, *operands)

@defun("-")
def subtract(ctx, *operands):
    """Negate one number or subtract many."""

    if len(operands) == 1:
        return -operands[0]
    else:
        return reduce(float, lambda x, y: x - y, *operands)

@defun("*")
def multiply(ctx, *operands):
    "Multiply numbers."
    return reduce(float, lambda x, y: x * y, *operands)

@defun("/")
def divide(ctx, *operands):
    "Divide numbers."
    return reduce(float, lambda x, y: x / y, *operands)

@defun("1+")
def add_one(ctx, x):
    """Same as (+ X 1)"""
    return add(ctx, x, 1)

@defun("1-")
def subtract_one(ctx, x):
    """Same as (- X 1)"""
    return subtract(ctx, x, 1)

@defun("above", "^")
def above(ctx, n=1):
    """Get the Nth cell above."""
    return at(ctx, row(ctx) - n, col(ctx))

@defun("below", "v")
def below(ctx, n=1):
    """Get the Nth cell below."""
    return above(ctx, -n)

@defun("left", "<")
def left(ctx, n=1):
    """Get the Nth cell to the left."""
    return at(ctx, row(ctx), col(ctx) - n)

@defun("right", ">")
def right(ctx, n=1):
    """Get the Nth cell to the right."""
    return left(ctx, -n)

@defun("range", "#")
class CellRange:
    """Get a range of cells between a start and end point."""

    def __init__(self, ctx, start_row, start_col, end_row, end_col):
        self.__ctx = ctx

        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col

        self.__iterator_row = self.start_row
        self.__iterator_col = self.start_col

    def __iter__(self):
        return self

    def __next__(self):
        if self.__iterator_row > self.end_row:
            self.__iterator_col += 1
            self.__iterator_row = self.start_row

        if self.__iterator_col > self.end_col:
            raise StopIteration

        cell = {
            "value": at(self.__ctx, self.__iterator_row, self.__iterator_col),
            "row": self.__iterator_row,
            "col": self.__iterator_col
        }

        self.__iterator_row += 1

        return cell

@defun("row", "_")
def row(ctx):
    """Get this cell's row."""
    return ctx["cell"].row

@defun("col", "|")
def col(ctx):
    """Get this cell's column."""
    return ctx["cell"].col

@defun("rows", ">|")
def rows(ctx):
    return len(ctx["table"].rows)

@defun("cols", ">_")
def cols(ctx):
    return len(ctx["table"].rows[0])

@defun("average", "avg")
def average(ctx, x, *rest):
    """Find the average value of X and the REST."""
    args = flatten([x, *rest])
    return divide(ctx, add(ctx, args), len(args))
