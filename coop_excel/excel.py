class Cell:
    def __init__(self, value):
        self.value = value

class Table:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rows = []

        for y in range(self.height):
            self.rows.append([])

            for x in range(self.width):
                self.rows[y].append(Cell(x + y))

    @property
    def values(self):
        values = []

        for row in self.rows:
            values.append([cell.value for cell in row])

        return values

table = Table(10, 50)
