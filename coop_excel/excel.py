import re
import copy

from .lisp import evaluate

class Cell:
    def __init__(self, expr, table, row, col):
        self.expression = expr
        self.table = table
        self.row = row
        self.col = col

    @property
    def expression(self):
        return self.__expression

    @expression.setter
    def expression(self, expr):
        self.__expression = str(expr)

    @property
    def value(self):
        split = re.split(r"=\s*(?!$)", self.expression, 2)

        if len(split) != 2:
            return self.expression

        ctx = {
            "recursion": 0,
            "table": self.table,
            "cell": self,
        }

        result = evaluate(ctx, split[1])

        if result is None:
            return "<ERROR>"
        else:
            return result

class Table:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rows = []
        self.last = []

        for row in range(self.height):
            self.rows.append([])

            for col in range(self.width):
                self.rows[-1].append(None)
                self.set(row, col, "= (* (row) (col))")

    def is_in_bounds(self, row, col):
        return row in range(self.height) and col in range(self.width)

    def get(self, row, col):
        if self.is_in_bounds(row, col):
            return self.rows[row][col]
        else:
            return Cell("", self, row, col)

    def set(self, row, col, expression):
        if self.is_in_bounds(row, col):
            self.rows[row][col] = Cell(expression, self, row, col)

    def delta(self, base=None):
        delta = []

        if base is None:
            base = self.last

        self.last = []

        for row, table_row in enumerate(self.rows):
            self.last.append([])

            for col, cell in enumerate(table_row):
                d = {
                    "expression": cell.expression,
                    "value": cell.value,
                    "row": row,
                    "col": col
                }

                if not base or base[row][col] != d:
                    delta.append(d)

                self.last[-1].append(d)

        return delta

table = Table(10, 50)
