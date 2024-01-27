from typing import Tuple, Optional

from PIL import ImageDraw, Image, ImageFont
from pilmoji import Pilmoji

from bot.constants import TEXT_FONT_SIZE, TEXT_REG_FONT, FILES_PATH
from bot.types.Point import Point
from bot.types.Size import Size
from bot.types.TextMode import TextMode

TEXT_IT_FONT = ImageFont.truetype(f"{FILES_PATH}/font_italic.ttf", TEXT_FONT_SIZE)
TEXT_BLD_FONT = ImageFont.truetype(f"{FILES_PATH}/font_bold.ttf", TEXT_FONT_SIZE)
TEXT_BLD_IT_FONT = ImageFont.truetype(
    f"{FILES_PATH}/font_bold_italic.ttf", TEXT_FONT_SIZE
)
TEXT_MONO_FONT = ImageFont.truetype(f"{FILES_PATH}/font_mono.ttf", TEXT_FONT_SIZE)


# https://stackoverflow.com/a/77749307/23112474
def get_text_size(text, font) -> Size:
    image = Image.new(mode="P", size=(0, 0))
    d = ImageDraw.Draw(image)
    _, _, width, height = d.textbbox((0, 0), text=text, font=font)
    return Size(width, height)


def draw_md_text(text: str, size: int, position: Point, canvas_size: Size) -> Image:
    canvas_result = Image.new(
        "RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0)
    )

    text_length = len(text)
    mods = []
    skip = False
    newline = False
    x = position.X
    y = position.Y

    for index, char in enumerate(text):
        if skip:
            skip = False
            continue

        char_image: Optional[Image] = None
        text_size: Optional[Size] = None

        match char:
            case "\\":
                if index + 1 < text_length:
                    skip = True
                    next_char = text[index + 1]
                    if next_char != "r":
                        if next_char == "n":
                            newline = True
                        else:
                            (text_size, char_image) = _draw_char(
                                next_char, size, canvas_size, Point(x, y), mods
                            )
                else:
                    (text_size, char_image) = _draw_char(
                        char, size, canvas_size, Point(x, y), mods
                    )
            case "~":
                if TextMode.STRIKE in mods:
                    mods.remove(TextMode.STRIKE)
                else:
                    mods.append(TextMode.STRIKE)
            case "`":
                if TextMode.CODE in mods:
                    mods.remove(TextMode.CODE)
                else:
                    mods.append(TextMode.CODE)
            case "*":
                if TextMode.BOLD in mods:
                    mods.remove(TextMode.BOLD)
                else:
                    mods.append(TextMode.BOLD)
            case "_":
                if index + 1 < text_length:
                    if text[index + 1] == "_":
                        skip = True
                        if TextMode.UNDERLINE in mods:
                            mods.remove(TextMode.UNDERLINE)
                        else:
                            mods.append(TextMode.UNDERLINE)
                    else:
                        if TextMode.ITALIC in mods:
                            mods.remove(TextMode.ITALIC)
                        else:
                            mods.append(TextMode.ITALIC)
            case "|":
                if index + 1 < text_length:
                    if text[index + 1] == "|":
                        skip = True
                        if TextMode.SPOILER in mods:
                            mods.remove(TextMode.SPOILER)
                        else:
                            mods.append(TextMode.SPOILER)

            case _:
                (text_size, char_image) = _draw_char(
                    char, size, canvas_size, Point(x, y), mods
                )

        if char_image:
            if newline:
                y += text_size.height
            else:
                x += text_size.width

            canvas_result = Image.alpha_composite(canvas_result, char_image)
            char_image = None
            text_size = None

    return canvas_result


def _draw_char(
    text: str, text_size: int, canvas_size: Size, position: Point, mods: list[TextMode]
) -> Tuple[Size, Image]:
    if TextMode.CODE in mods:
        font = TEXT_MONO_FONT
    else:
        if TextMode.BOLD in mods and TextMode.ITALIC in mods:
            font = TEXT_BLD_IT_FONT
        elif TextMode.BOLD in mods:
            font = TEXT_BLD_FONT
        elif TextMode.ITALIC in mods:
            font = TEXT_IT_FONT
        else:
            font = TEXT_REG_FONT

    font.size = text_size

    text_size = get_text_size(text, font)
    text_size.height += 2

    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    pij = Pilmoji(canvas)

    if TextMode.CODE in mods:
        d.rectangle(
            (
                position.X,
                position.Y,
                position.X + text_size.width,
                position.Y + TEXT_FONT_SIZE,
            ),
            fill="#773838",
        )
        d.text(
            (position.X, position.Y),
            text,
            fill="white",
            font=font,
        )
    else:
        if TextMode.SPOILER in mods:
            d.rectangle(
                (
                    position.X,
                    position.Y,
                    position.X + text_size.width,
                    position.Y + TEXT_FONT_SIZE,
                ),
                fill="#5b5b5b",
            )

        pij.text(
            (position.X, position.Y),
            text,
            fill="white",
            font=font,
        )

        if TextMode.STRIKE in mods:
            d.rectangle(
                (
                    position.X,
                    position.Y + int((TEXT_FONT_SIZE + 5) / 2),
                    position.X + text_size.width,
                    position.Y + int((TEXT_FONT_SIZE + 5) / 2),
                ),
                fill="white",
            )
        if TextMode.UNDERLINE in mods:
            d.rectangle(
                (
                    position.X,
                    position.Y + text_size.height,
                    position.X + text_size.width,
                    position.Y + text_size.height,
                ),
                fill="white",
            )

    return text_size, canvas
