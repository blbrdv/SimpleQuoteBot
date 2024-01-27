from PIL import Image
from pilmoji import Pilmoji

from bot.constants import PFP_WIDTH, TEXT_REG_FONT, FILES_PATH, INITIALS_FONT_SIZE, MARGIN
from bot.text import get_text_size
from bot.types.ColorScheme import ColorScheme
from bot.types.Point import Point
from bot.types.Size import Size


def generate_avatar(
    text: str, color: ColorScheme, coordinates: Point, canvas_size: Size
) -> Image:
    size = Size(PFP_WIDTH, PFP_WIDTH)
    text_size = get_text_size(text, TEXT_REG_FONT)

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
