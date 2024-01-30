from bot.types.ColorScheme import ColorScheme
from bot.types.RGB import RGB


def get_color(user_id: int) -> ColorScheme:
    colors = [
        ColorScheme(RGB(255, 81, 106), RGB(255, 136, 94)),
        ColorScheme(RGB(255, 168, 92), RGB(255, 205, 106)),
        ColorScheme(RGB(214, 105, 237), RGB(224, 162, 243)),
        ColorScheme(RGB(84, 203, 104), RGB(160, 222, 126)),
        ColorScheme(RGB(40, 201, 183), RGB(83, 237, 214)),
        ColorScheme(RGB(42, 158, 241), RGB(114, 213, 253)),
        ColorScheme(RGB(255, 113, 154), RGB(255, 168, 168)),
    ]

    return colors[abs(user_id) % 7]
