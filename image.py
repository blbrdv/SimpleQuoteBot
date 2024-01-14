from PIL import Image, ImageDraw


def draw(name: str):
    bg_raw = Image.open("bg.png").convert("RGBA")
    bg = bg_raw.resize((400, 400))
    image = Image.new("RGBA", (400, 400), (0, 0, 0))
    canvas = image.copy()

    canvas.paste(bg)

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(
        (10, 10, 50, 50), radius=5, fill="#202123", corners=(True, True, True, False)
    )

    canvas.save(name)
