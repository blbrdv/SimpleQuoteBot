from PIL import Image, ImageDraw, ImageFont

from ColorScheme import ColorScheme
from Message import Message
from Point import Point
from RGB import RGB
from Size import Size
from Speech import Speech

TEXT_FONT_SIZE = 20
TIME_FONT_SIZE = 15
INITIALS_FONT_SIZE = 32
TEXT_FONT = ImageFont.truetype("font.ttf", TEXT_FONT_SIZE)
TIME_FONT = ImageFont.truetype("font.ttf", TIME_FONT_SIZE)
INITIALS_FONT = ImageFont.truetype("font.ttf", INITIALS_FONT_SIZE)
MAX_CANVAS_WIDTH = 512
MARGIN = 10
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

    bg_raw = Image.open("bg.png").convert("RGBA")
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
    for message in speech.messages:
        message_image = _draw_message(
            message,
            canvas_size,
            message_image_y,
            _get_color(speech.author.user_id).primary,
        )

        canvas = Image.alpha_composite(canvas, message_image)

        message_size = _message_size(message)
        message_image_y += message_size.height + TOTAL_MARGIN

    pfp = _generate_avatar(
        speech.author.initials,
        _get_color(speech.author.user_id),
        Point(MARGIN, speech_image_y + speech_size.height - PFP_WIDTH),
        canvas_size,
    )
    canvas = Image.alpha_composite(canvas, pfp)

    return canvas


def _draw_message(
    message: Message, canvas_size: Size, y: int, header_color: RGB
) -> Image:
    message_size = _message_size(message)
    text_size = _text_size(message.text, TEXT_FONT)
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)

    d.rounded_rectangle(
        (
            TOTAL_MARGIN * 2 + PFP_WIDTH,
            y,
            TOTAL_MARGIN + message_size.width + PFP_WIDTH,
            y + message_size.height,
        ),
        radius=5,
        fill="#202123",
        corners=(True, True, True, not message.is_last),
    )
    if message.is_last:
        d.polygon(
            [
                (TOTAL_MARGIN * 2 + PFP_WIDTH, y + message_size.height),
                (TOTAL_MARGIN * 2 + PFP_WIDTH, y + message_size.height - 8),
                (TOTAL_MARGIN * 2 + PFP_WIDTH - 10, y + message_size.height),
            ],
            fill="#202123",
        )

    text_y = y + MARGIN
    if message.is_first:
        d.text(
            (TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, y + MARGIN),
            message.header,
            fill=header_color.value,
            font=TEXT_FONT,
        )
        text_y += TEXT_FONT_SIZE + MARGIN
    d.text(
        (TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, text_y),
        message.text,
        fill="white",
        font=TEXT_FONT,
    )
    d.text(
        (
            TOTAL_MARGIN * 2 + MARGIN * 2 + PFP_WIDTH + text_size.width,
            text_y + int(TIME_FONT_SIZE / 2),
        ),
        message.time,
        fill="grey",
        font=TIME_FONT,
    )

    return canvas


def _speech_size(speech: Speech) -> Size:
    canvas_height = 0
    canvas_width = 0

    for message in speech.messages:
        message_size = _message_size(message)

        canvas_height += message_size.height + TOTAL_MARGIN
        if message_size.width + TOTAL_MARGIN > canvas_width:
            canvas_width = message_size.width + TOTAL_MARGIN

    return Size(canvas_width, canvas_height)


def _message_size(message: Message) -> Size:
    text_size = _text_size(message.text, TEXT_FONT)
    time_size = _text_size(message.time, TIME_FONT)

    width = text_size.width + TOTAL_MARGIN + TOTAL_MARGIN + time_size.width + MARGIN
    height = text_size.height + int(time_size.height / 2)

    if message.is_first:
        user_name_size = _text_size(message.header, TEXT_FONT)
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
    return Size(width, TEXT_FONT_SIZE)


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
    text_size = _text_size(text, INITIALS_FONT)

    canvas_result = Image.new(
        "RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0)
    )
    canvas_transparent = Image.new("RGBA", (size.width, size.height), (0, 0, 0, 0))
    mask = Image.open("pfp_mask.png").convert("L")
    gradient = _generate_gradient(color, size).convert("RGBA")

    pfp = Image.composite(canvas_transparent, gradient, mask)
    pfp_d = ImageDraw.Draw(pfp)
    pfp_d.text(
        (
            int(PFP_WIDTH / 2) - int(text_size.width / 2),
            int(PFP_WIDTH / 2) - int(INITIALS_FONT_SIZE / 2) + int(MARGIN / 2),
        ),
        text,
        fill="white",
        font=INITIALS_FONT,
    )

    canvas_result.paste(pfp, (coordinates.X, coordinates.Y))
    canvas_result.save("test2.png", format="png")

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


# def _break_fix(text, width, font, draw):
#     if not text:
#         return
#     lo = 0
#     hi = len(text)
#     while lo < hi:
#         mid = (lo + hi + 1) // 2
#         t = text[:mid]
#         w, h = _text_size(t, font=font)
#         if w <= width:
#             lo = mid
#         else:
#             hi = mid - 1
#     t = text[:lo]
#     w, h = _text_size(t, font=font)
#     yield t, w, h
#     yield from _break_fix(text[lo:], width, font, draw)
#
#
# # https://stackoverflow.com/a/58176967/23112474
# def _fit_text(img, text, color, font):
#     width = img.size[0] - 2
#     draw = ImageDraw.Draw(img)
#     pieces = list(_break_fix(text, width, font, draw))
#     height = sum(p[2] for p in pieces)
#     if height > img.size[1]:
#         raise ValueError("text doesn't fit")
#     y = (img.size[1] - height) // 2
#     for t, w, h in pieces:
#         x = (img.size[0] - w) // 2
#         draw.text((x, y), t, font=font, fill=color)
#         y += h
