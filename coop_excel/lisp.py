import re

functions = {}

def evaluate(table, expression):
    form = re.fullmatch(r"\((?P<form>.*)\)", expression)

    if not form:
        return cast(expression)

    form = re.findall(r"\(.*?\)|[^\s]+", form.group("form"))

    fun = form[0]
    args = form[1:] if len(form) > 1 else []

    if fun in functions:
        try:
            args = [evaluate(table, arg) for arg in args]
            return cast(functions[fun](table, *args))
        except:
            return None

    return None

def cast(expr):
    expr = str(expr)

    string_match = re.fullmatch(r'(?<=\").*(?=\")', expr)

    if string_match:
        return string_match.group(0)

    try:
        if float(expr) == int(expr):
            return int(expr)
        else:
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
    if isinstance(row, int) and isinstance(col, int):
        return table.get(row, col).value

@lisp_fn("+")
def plus(table, *args):
    s = 0

    for x in args:
        s += x

    return s
