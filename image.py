from PIL import Image, ImageDraw, ImageFont

from utils import text_size


TEXT_FONT = ImageFont.truetype("font.ttf", 14)
MAX_CANVAS_WIDTH = 512
PADDING = 10
TOTAL_PADDING = PADDING * 2


def draw(messages: list[str], name: str) -> None:
    canvas_height = TOTAL_PADDING
    canvas_width = 0

    for message in messages:
        (width, height) = _message_size(message)

        canvas_height += height
        if width > canvas_width:
            canvas_width = width

    bg_raw = Image.open("bg.png").convert("RGBA")
    bg = bg_raw.resize((canvas_width + TOTAL_PADDING, canvas_height + TOTAL_PADDING))
    canvas = Image.new(
        "RGBA", (canvas_width + TOTAL_PADDING, canvas_height + TOTAL_PADDING), (0, 0, 0)
    )
    canvas.paste(bg)

    message_image_y = PADDING
    for message in messages:
        message_image = _draw_message(
            message,
            (canvas_width + TOTAL_PADDING, canvas_height + TOTAL_PADDING),
            message_image_y,
        )

        canvas = Image.alpha_composite(canvas, message_image)

        (_, message_image_height) = _message_size(message)
        message_image_y += message_image_height + PADDING

    canvas.save(name)


def _message_size(text: str) -> tuple[int, int]:
    (text_width, text_height) = text_size(text, TEXT_FONT)

    return text_width + TOTAL_PADDING + PADDING, text_height + TOTAL_PADDING


def _draw_message(text: str, size: tuple[int, int], y: int) -> Image:
    (canvas_width, canvas_height) = _message_size(text)
    canvas = Image.new("RGBA", (size[0], size[1]), (0, 0, 0, 0))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(
        (PADDING, y, canvas_width, y + canvas_height),
        radius=5,
        fill="#202123",
        corners=(True, True, True, False),
    )
    d.text((TOTAL_PADDING, y + PADDING), text, fill="white", font=TEXT_FONT)

    return canvas
