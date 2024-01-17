from PIL import Image, ImageDraw, ImageFont


TEXT_FONT = ImageFont.truetype("font.ttf", 14)
TIME_FONT = ImageFont.truetype("font.ttf", 10)
MAX_CANVAS_WIDTH = 512
MARGIN = 5
TOTAL_MARGIN = MARGIN * 2


def draw(messages: list[tuple[str, str]], name: str) -> None:
    canvas_height = MARGIN
    canvas_width = 0

    for message, time in messages:
        (width, height) = _message_size(message, time)

        canvas_height += height + TOTAL_MARGIN
        if width + TOTAL_MARGIN > canvas_width:
            canvas_width = width + TOTAL_MARGIN

    bg_raw = Image.open("bg.png").convert("RGBA")
    bg = bg_raw.resize((canvas_width, canvas_height))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0))
    canvas.paste(bg)

    message_image_y = MARGIN
    for message, time in messages:
        message_image = _draw_message(
            message,
            time,
            (canvas_width, canvas_height),
            message_image_y,
        )

        canvas = Image.alpha_composite(canvas, message_image)

        (_, message_image_height) = _message_size(message, time)
        message_image_y += message_image_height + TOTAL_MARGIN

    canvas.save(name)


def _draw_message(text: str, time: str, size: tuple[int, int], y: int) -> Image:
    (block_width, block_height) = _message_size(text, time)
    (text_width, _) = _text_size(text, TEXT_FONT)

    canvas = Image.new("RGBA", (size[0], size[1]), (0, 0, 0, 0))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(
        (MARGIN, y, block_width, y + block_height),
        radius=5,
        fill="#202123",
        corners=(True, True, True, False),
    )
    d.text((TOTAL_MARGIN, y + MARGIN), text, fill="white", font=TEXT_FONT)
    d.text((text_width + TOTAL_MARGIN + MARGIN, y + int(block_height / 2)), time, fill="grey", font=TIME_FONT)

    return canvas


def _message_size(text: str, time: str) -> tuple[int, int]:
    (text_width, text_height) = _text_size(text, TEXT_FONT)
    (datetime_width, datetime_height) = _text_size(time, TIME_FONT)

    return (
        text_width + datetime_width + TOTAL_MARGIN + TOTAL_MARGIN,
        text_height + TOTAL_MARGIN + int((datetime_height / 2)),
    )


# https://stackoverflow.com/a/77749307/23112474
def _text_size(text, font):
    image = Image.new(mode="P", size=(0, 0))
    d = ImageDraw.Draw(image)
    _, _, width, height = d.textbbox((0, 0), text=text, font=font)
    return width, height


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
