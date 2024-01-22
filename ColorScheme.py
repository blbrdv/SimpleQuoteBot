from RGB import RGB


class ColorScheme:
    def __init__(self, primary: RGB, secondary: RGB):
        self.primary = primary
        self.secondary = secondary

    primary: RGB
    secondary: RGB
