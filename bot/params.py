from enum import Enum


class Theme(Enum):
    LIGHT = 0
    DARK = 1


class Params:
    def __init__(self, theme: Theme, is_anon: bool):
        self.theme = theme
        self.is_anon = is_anon

    theme: Theme
    is_anon: bool
