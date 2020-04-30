from .cell import Cell

class Table:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rows = []

        for y in range(self.height):
            self.rows.append([])

            for x in range(self.width):
                self.rows[y].append(Cell(x + y, self))

    def is_in_bounds(self, row, col):
        return row in range(self.height) and col in range(self.width)

    def get(self, row, col):
        if self.is_in_bounds(row, col):
            return self.rows[row][col]
        else:
            return Cell("", self)

    def set(self, row, col, expression):
        if self.is_in_bounds(row, col):
            cell = self.get(row, col)
            cell.expression = expression
            return cell.expression, cell.value

    @property
    def networked(self):
        values = []

        for row in self.rows:
            values.append([{
                "value": cell.value,
                "expression": cell.expression
            } for cell in row])

        return values

table = Table(10, 50)
