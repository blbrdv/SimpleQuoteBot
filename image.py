from PIL import Image, ImageDraw, ImageFont

from utils import text_size, fit_text


def draw(messages: list[str], name: str):
    bg_raw = Image.open("bg.png").convert("RGBA")
    bg = bg_raw.resize((512, 512))
    image = Image.new("RGBA", (512, 512), (0, 0, 0))
    canvas = image.copy()

    canvas.paste(bg)

    font = ImageFont.truetype("font.ttf", 14)
    d = ImageDraw.Draw(canvas)

    for message in messages:
        (w, _) = text_size(message, font)

        d.rounded_rectangle(
            (10, 10, 492, 50), radius=5, fill="#202123", corners=(True, True, True, False)
        )

        if w > 472:
            fit_text(canvas, message, "white", font)
        else:
            d.text((20, 20), message, "white", font)

    canvas.save(name)
