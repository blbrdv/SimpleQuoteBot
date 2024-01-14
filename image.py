from PIL import Image, ImageDraw


def draw(name: str):
    image = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)

    d.rounded_rectangle(
        (10, 10, 50, 50), radius=5, fill="#202123", corners=(True, True, True, False)
    )

    image.save(name)
