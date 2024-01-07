from PIL import Image, ImageDraw


def draw():
    image = Image.new("RGB", (400, 400), "white")
    d = ImageDraw.Draw(image)

    d.rounded_rectangle((10, 10, 50, 50), radius=5, fill="#202123", corners=(True, True, True, False))

    image.save("test.jpg")

