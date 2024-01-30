from PIL import Image, ImageFont
from pilmoji import Pilmoji

from bot.constants import PFP_WIDTH, FILES_PATH, RGBA_ZERO
from bot.text import get_text_size
from bot.types.ColorScheme import ColorScheme
from bot.types.Point import Point
from bot.types.Size import Size

INITIALS_FONT_SIZE = 30
INITIALS_FONT = ImageFont.truetype(f"{FILES_PATH}/font_regular.ttf", INITIALS_FONT_SIZE)


def generate_avatar(
    text: str, color: ColorScheme, coordinates: Point, canvas_size: Size
) -> Image:
    size = Size(PFP_WIDTH, PFP_WIDTH)
    text_size = get_text_size(text, INITIALS_FONT)

    canvas_result = Image.new(
        "RGBA", (canvas_size.width, canvas_size.height), RGBA_ZERO
    )
    canvas_transparent = Image.new("RGBA", (size.width, size.height), RGBA_ZERO)
    mask = Image.open(f"{FILES_PATH}/pfp_mask.png").convert("L")
    gradient = _generate_gradient(color, size).convert("RGBA")

    pfp = Image.composite(canvas_transparent, gradient, mask)
    pij = Pilmoji(pfp)
    pij.text(
        (
            int(PFP_WIDTH / 2) - int(text_size.width / 2),
            int(PFP_WIDTH / 2) - int(INITIALS_FONT_SIZE / 2),
        ),
        text,
        fill="white",
        font=INITIALS_FONT,
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
