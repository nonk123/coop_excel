import re

SYMBOL = r"[A-Za-z0-9_]+"
SEP = r"(?:\s*)"

def index(name):
    return "(?P<{0}_abs>\$)?(?P<{0}>[0-9]+)".format(name)

def addr(prefix=""):
    return f"{index(prefix + 'col')}:{index(prefix + 'row')}"

REF = f"{addr()}"
RANGE = f"{addr('start_')}-{addr('end_')}"

def ref(table, row, col):
    try:
        return table.get(int(row), int(col)).value
    except:
        return None

def symbol(table, symbol):
    return symbol

class Cell:
    def __init__(self, expr, table):
        self.expression = expr
        self.table = table

    @property
    def expression(self):
        return self.__expression

    @expression.setter
    def expression(self, expr):
        self.__expression = str(expr)

    @property
    def value(self):
        split = re.split(f"={SEP}(?!$)", self.expression, 2)

        if len(split) != 2:
            return self.expression

        parsers = {
            f"(?P<symbol>{SYMBOL})": symbol,
            REF: ref
        }

        for pattern, parser in parsers.items():
            match = re.fullmatch(pattern, split[1].strip())

            if match:
                kwargs = {}

                args = parser.__code__.co_varnames[1:parser.__code__.co_argcount]

                for var in args:
                    kwargs[var] = match.group(var)

                value = parser(self.table, **kwargs)

                return "<ERROR>" if value is None else value

        return self.expression
