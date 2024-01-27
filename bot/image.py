import os

from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

from .types.ColorScheme import ColorScheme
from .types.Message import Message
from .types.Point import Point
from .types.RGB import RGB
from .types.Size import Size
from .types.Speech import Speech
from .types.TextMode import TextMode

TEXT_FONT_SIZE = 20
TIME_FONT_SIZE = 15
INITIALS_FONT_SIZE = 32
FILES_PATH = f"{os.getcwd()}/files"
TEXT_REG_FONT = ImageFont.truetype(f"{FILES_PATH}/font_regular.ttf", TEXT_FONT_SIZE)
TEXT_IT_FONT = ImageFont.truetype(f"{FILES_PATH}/font_italic.ttf", TEXT_FONT_SIZE)
TEXT_BLD_FONT = ImageFont.truetype(f"{FILES_PATH}/font_bold.ttf", TEXT_FONT_SIZE)
TEXT_BLD_IT_FONT = ImageFont.truetype(
    f"{FILES_PATH}/font_bold_italic.ttf", TEXT_FONT_SIZE
)
TEXT_MONO_FONT = ImageFont.truetype(f"{FILES_PATH}/font_mono.ttf", TEXT_FONT_SIZE)
MARGIN = 12
TOTAL_MARGIN = MARGIN * 2
PFP_WIDTH = 75


def draw(data: list[Speech], name: str) -> None:
    canvas_height = TOTAL_MARGIN
    canvas_width = PFP_WIDTH

    for speech in data:
        speech_size = _speech_size(speech)

        canvas_height += speech_size.height
        full_width = speech_size.width + TOTAL_MARGIN + PFP_WIDTH
        if full_width > canvas_width:
            canvas_width = full_width

    bg_raw = Image.open(f"{FILES_PATH}/bg.png").convert("RGBA")
    bg = bg_raw.resize((canvas_width, canvas_height))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0))
    canvas.paste(bg)

    speech_image_y = 0
    for speech in data:
        speech_size = _speech_size(speech)
        speech_image = _draw_speech(
            speech, Size(canvas_width, canvas_height), speech_image_y
        )

        canvas = Image.alpha_composite(canvas, speech_image)

        speech_image_y += speech_size.height

    canvas.save(name)


def _draw_speech(speech: Speech, canvas_size: Size, speech_image_y: int) -> Image:
    speech_size = _speech_size(speech)
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))

    message_image_y = TOTAL_MARGIN + speech_image_y
    for index, message in enumerate(speech.messages):
        message_image = _draw_message(
            message,
            canvas_size,
            message_image_y,
            _get_color(speech.author.user_id).primary,
            index == 0,
        )

        canvas = Image.alpha_composite(canvas, message_image)

        message_size = _message_size(message, index == 0)
        message_image_y += message_size.height + TOTAL_MARGIN

    pfp = _generate_avatar(
        speech.author.initials,
        _get_color(speech.author.user_id),
        Point(MARGIN, MARGIN + speech_image_y + speech_size.height - PFP_WIDTH),
        canvas_size,
    )
    canvas = Image.alpha_composite(canvas, pfp)

    return canvas


def _draw_message(
    message: Message, canvas_size: Size, y: int, header_color: RGB, is_first: bool
) -> Image:
    message_size = _message_size(message, is_first)
    text_size = _text_size(message.text, TEXT_REG_FONT)
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    pij = Pilmoji(canvas)

    rectangle_y = y + message_size.height + MARGIN
    d.rounded_rectangle(
        (
            TOTAL_MARGIN * 2 + PFP_WIDTH,
            y,
            TOTAL_MARGIN + message_size.width + PFP_WIDTH,
            rectangle_y,
        ),
        radius=5,
        fill="#202123",
        corners=(True, True, True, not message.is_last),
    )
    if message.is_last:
        d.polygon(
            [
                (TOTAL_MARGIN * 2 + PFP_WIDTH, rectangle_y),
                (TOTAL_MARGIN * 2 + PFP_WIDTH, rectangle_y - 8),
                (TOTAL_MARGIN * 2 + PFP_WIDTH - 10, rectangle_y),
            ],
            fill="#202123",
        )

    text_y = y + MARGIN
    if message.is_first:
        pij.text(
            (TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, y + MARGIN),
            message.header,
            fill=header_color.value,
            font=TEXT_REG_FONT,
        )
        text_y += TEXT_FONT_SIZE + MARGIN

    d.text(
        (
            TOTAL_MARGIN * 2 + MARGIN * 2 + PFP_WIDTH + text_size.width,
            rectangle_y - TOTAL_MARGIN - int(TIME_FONT_SIZE / 2),
        ),
        message.time,
        fill="grey",
        font=TEXT_REG_FONT,
    )

    text_image = _draw_md_text(
        message.text,
        TEXT_FONT_SIZE,
        Point(TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, text_y),
        canvas_size,
    )
    canvas = Image.alpha_composite(canvas, text_image)

    return canvas


def _speech_size(speech: Speech) -> Size:
    canvas_height = 0
    canvas_width = 0

    for index, message in enumerate(speech.messages):
        message_size = _message_size(message, index == 0)

        canvas_height += message_size.height + TOTAL_MARGIN
        if message_size.width + TOTAL_MARGIN > canvas_width:
            canvas_width = message_size.width + TOTAL_MARGIN

    return Size(canvas_width, canvas_height)


def _message_size(message: Message, is_first: bool) -> Size:
    text_size = _text_size(message.text, TEXT_REG_FONT)
    time_size = _text_size(message.time, TEXT_REG_FONT)

    width = text_size.width + TOTAL_MARGIN + TOTAL_MARGIN + time_size.width + MARGIN
    height = text_size.height + int(time_size.height / 2)

    if not is_first:
        height += MARGIN

    if message.is_first:
        user_name_size = _text_size(message.header, TEXT_REG_FONT)
        user_name_width = user_name_size.width + TOTAL_MARGIN + TOTAL_MARGIN

        if user_name_width > width:
            width = user_name_width
        height += user_name_size.height + TOTAL_MARGIN

    return Size(width, height)


# https://stackoverflow.com/a/77749307/23112474
def _text_size(text, font) -> Size:
    image = Image.new(mode="P", size=(0, 0))
    d = ImageDraw.Draw(image)
    _, _, width, height = d.textbbox((0, 0), text=text, font=font)
    return Size(width, height)


def _get_color(user_id: int) -> ColorScheme:
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


def _generate_avatar(
    text: str, color: ColorScheme, coordinates: Point, canvas_size: Size
) -> Image:
    size = Size(PFP_WIDTH, PFP_WIDTH)
    text_size = _text_size(text, TEXT_REG_FONT)

    canvas_result = Image.new(
        "RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0)
    )
    canvas_transparent = Image.new("RGBA", (size.width, size.height), (0, 0, 0, 0))
    mask = Image.open(f"{FILES_PATH}/pfp_mask.png").convert("L")
    gradient = _generate_gradient(color, size).convert("RGBA")

    pfp = Image.composite(canvas_transparent, gradient, mask)
    pij = Pilmoji(pfp)
    pij.text(
        (
            int(PFP_WIDTH / 2) - int(text_size.width / 2),
            int(PFP_WIDTH / 2) - int(INITIALS_FONT_SIZE / 2) + int(MARGIN / 2),
        ),
        text,
        fill="white",
        font=TEXT_REG_FONT,
    )

    canvas_result.paste(pfp, (coordinates.X, coordinates.Y))

    return canvas_result


# https://stackoverflow.com/a/63138452/23112474
def _generate_gradient(color: ColorScheme, size: Size) -> Image:
    base = Image.new("RGB", (size.width, size.height), color.secondary.value)
    top = Image.new("RGB", (size.width, size.height), color.primary.value)
    mask = Image.new("L", (size.width, size.height))
    mask_data = []

    for y in range(size.height):
        mask_data.extend([int(255 * (y / size.height))] * size.width)

    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)

    return base


def _draw_md_text(text: str, size: int, position: Point, canvas_size: Size) -> Image:
    canvas_result = Image.new(
        "RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0)
    )

    text_length = len(text)
    mods = []
    skip = False
    newline = False
    x = position.X
    y = position.Y
    last_y = 0

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

    text_size = _text_size(text, font)
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
