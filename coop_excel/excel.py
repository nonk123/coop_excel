class Cell:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.__value = int(value)
        except:
            self.__value = value

class Table:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.rows = []

        for y in range(self.height):
            self.rows.append([])

            for x in range(self.width):
                self.rows[y].append(Cell(x + y))

    def is_in_bounds(self, row, col):
        return row in range(self.height) and col in range(self.width)

    def get(self, row, col):
        if self.is_in_bounds(row, col):
            return self.rows[row][col]
        else:
            return Cell("")

    def set(self, row, col, value):
        if self.is_in_bounds(row, col):
            self.rows[row][col].value = value

    @property
    def values(self):
        values = []

        for row in self.rows:
            values.append([cell.value for cell in row])

        return values

table = Table(10, 50)
