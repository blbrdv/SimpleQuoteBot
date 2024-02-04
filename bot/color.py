class Color:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue
        self.hex = "#%02x%02x%02x" % (red, green, blue)

    red: int
    green: int
    blue: int
    hex: str

    @property
    def value(self) -> tuple[int, int, int]:
        return self.red, self.green, self.blue


class ColorScheme:
    def __init__(self, primary: Color, secondary: Color):
        self.primary = primary
        self.secondary = secondary

    primary: Color
    secondary: Color


COLORS = [
    ColorScheme(Color(255, 81, 106), Color(255, 136, 94)),
    ColorScheme(Color(255, 168, 92), Color(255, 205, 106)),
    ColorScheme(Color(214, 105, 237), Color(224, 162, 243)),
    ColorScheme(Color(84, 203, 104), Color(160, 222, 126)),
    ColorScheme(Color(40, 201, 183), Color(83, 237, 214)),
    ColorScheme(Color(42, 158, 241), Color(114, 213, 253)),
    ColorScheme(Color(255, 113, 154), Color(255, 168, 168)),
]


def get_color(user_id: int) -> ColorScheme:
    return COLORS[abs(user_id) % 7]
