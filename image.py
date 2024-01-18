from PIL import Image, ImageDraw, ImageFont

from Message import Message
from Size import Size
from Speech import Speech

TEXT_FONT = ImageFont.truetype("font.ttf", 14)
MAX_CANVAS_WIDTH = 512
MARGIN = 5
TOTAL_MARGIN = MARGIN * 2


def draw(data: list[Speech], name: str) -> None:
    canvas_height = MARGIN
    canvas_width = 50

    for speech in data:
        speech_size = _speech_size(speech)

        canvas_height += speech_size.height + TOTAL_MARGIN
        full_width = speech_size.width + TOTAL_MARGIN + 50
        if full_width > canvas_width:
            canvas_width = full_width

    bg_raw = Image.open("bg.png").convert("RGBA")
    bg = bg_raw.resize((canvas_width, canvas_height))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0))
    canvas.paste(bg)

    speech_image_y = 0
    for speech in data:
        speech_image = _draw_speech(
            speech, Size(canvas_width, canvas_height), speech_image_y
        )

        canvas = Image.alpha_composite(canvas, speech_image)

        speech_image_y += speech_image_y

    canvas.save(name)


def _draw_speech(
    speech: Speech, canvas_size: Size, speech_image_y: int
) -> Image:
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))

    count = 1
    message_image_y = TOTAL_MARGIN + speech_image_y
    for message in speech.messages:
        message_image = _draw_message(
            message,
            canvas_size,
            message_image_y,
            count == len(speech.messages),
        )

        canvas = Image.alpha_composite(canvas, message_image)

        message_size = _message_size(message)
        message_image_y += message_size.height + TOTAL_MARGIN

        count += 1

    return canvas


def _draw_message(
    message: Message, canvas_size: Size, y: int, last: bool = False
) -> Image:
    message_size = _message_size(message)

    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))

    d = ImageDraw.Draw(canvas)

    d.rounded_rectangle(
        (MARGIN, y, message_size.width, y + message_size.height),
        radius=5,
        fill="#202123",
        corners=(True, True, True, not last),
    )
    # if last:
    #     d.polygon([(20, 10), (200, 200), (100, 20)], fill=(255, 0, 0))

    d.text((TOTAL_MARGIN, y + MARGIN), message.text, fill="white", font=TEXT_FONT)

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

    return Size(
        text_size.width + TOTAL_MARGIN + TOTAL_MARGIN,
        text_size.height + TOTAL_MARGIN,
    )


# https://stackoverflow.com/a/77749307/23112474
def _text_size(text, font) -> Size:
    image = Image.new(mode="P", size=(0, 0))
    d = ImageDraw.Draw(image)
    _, _, width, height = d.textbbox((0, 0), text=text, font=font)
    return Size(width, height)


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
