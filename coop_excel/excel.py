import re

from .lisp import evaluate

class Cell:
    def __init__(self, expr, table, row, col):
        self.__dependants = []

        self.expression = expr
        self.table = table
        self.row = row
        self.col = col

    @property
    def dependants(self):
        return self.__dependants

    @property
    def expression(self):
        return self.__expression

    def __reset_dependants(self):
        self.__cached_value = None

        dependants_copy = [x for x in self.dependants]

        self.dependants.clear()

        for cell in dependants_copy:
            if cell.dependants:
                cell.__reset_dependants()
            else:
                cell.__cached_value = None

    @expression.setter
    def expression(self, expr):
        self.__expression = str(expr)
        self.__reset_dependants()

    def get_value(self, recursion=0):
        if self.__cached_value is not None:
            return self.__cached_value

        match = re.fullmatch(r"=\s*(.+)", self.expression)

        if not match:
            return self.expression

        ctx = {
            "table": self.table,
            "cell": self,
            "recursion": recursion
        }

        try:
            value = evaluate(ctx, match[1])

            try:
                for new in iter(value):
                    row = self.row + new["row"] - value.start_row
                    col = self.col + new["col"] - value.start_col

                    self.table.get(row, col).__cached_value = new["value"]
            except TypeError:
                self.__cached_value = value

            return self.__cached_value
        except Exception as e:
            self.__cached_value = None
            return str(e)

    @property
    def stripped(self):
        return {
            "expression": self.expression,
            "value": self.get_value(),
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
                self.rows[row][col] = Cell("", self, row, col)

    def is_in_bounds(self, row, col):
        return row in range(self.height) and col in range(self.width)

    def get(self, row, col):
        try:
            return self.rows[row][col]
        except:
            return Cell("", self, row, col)

    def set(self, row, col, expr):
        if self.is_in_bounds(row, col):
            self.rows[row][col].expression = expr

    def set_stripped(self, cell):
        self.set(int(cell["row"]), int(cell["col"]), cell["expression"])

    def fill_with_stripped(self, stripped):
        for cell in stripped:
            self.set_stripped(cell)

    @property
    def _empty_flat(self):
        for i in range(len(self.rows) * len(self.rows[0])):
            yield {}

    @property
    def flat(self):
        for row in self.rows:
            for cell in row:
                yield cell.row, cell.col, cell

    def delta(self, base=None):
        delta = []

        if not self.last:
            self.last = self._empty_flat

        if base is None:
            base = self.last
        elif len(base) == 0:
            base = self._empty_flat

        this = []

        for row, col, old in self.flat:
            new = self.get(row, col).stripped

            if old != new:
                delta.append(new)

            this.append(new)

        self.last = this

        return delta

table = Table(10, 50)
