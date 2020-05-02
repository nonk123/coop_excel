import re

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

    @property
    def stripped(self):
        return {
            "expression": self.expression,
            "value": self.value,
            "row": self.row,
            "col": self.col
        }

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
                self.set(row, col, row * col)

    def is_in_bounds(self, row, col):
        return row in range(self.height) and col in range(self.width)

    def get(self, row, col):
        if self.is_in_bounds(row, col):
            return self.rows[row][col]
        else:
            return Cell("", self, row, col)

    def set(self, row, col, expr):
        self.rows[row][col] = Cell(expr, self, row, col)

    def update_with_stripped(self, stripped):
        for cell in stripped:
            row = int(cell["row"])
            col = int(cell["col"])

            if self.is_in_bounds(row, col):
                self.set(row, col, cell["expression"])

    @property
    def _empty_stripped(self):
        empty = []

        for table_row in self.rows:
            empty.append([{} for x in enumerate(table_row)])

        return empty

    def delta(self, base=None):
        delta = []

        if not self.last:
            self.last = self._empty_stripped

        if base is None:
            base = self.last
        elif len(base) == 0:
            base = self._empty_stripped

        this = []

        for row, table_row in enumerate(base):
            this.append([])

            for col, old in enumerate(table_row):
                new = self.get(row, col).stripped

                if old != new:
                    delta.append(new)

                this[-1].append(new)

        self.last = this

        return delta

table = Table(10, 50)
