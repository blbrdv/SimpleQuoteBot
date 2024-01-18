class RGB:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    red: int
    green: int
    blue: int

    @property
    def value(self) -> tuple[int, int, int]:
        return self.red, self.green, self.blue
