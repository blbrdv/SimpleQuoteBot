from PIL import Image

from .constants import FILES_PATH, TOTAL_MARGIN, PFP_WIDTH
from .speech import draw_speech, get_speech_size
from .types.Size import Size
from .types.Speech import Speech


def draw(data: list[Speech], name: str) -> None:
    canvas_height = TOTAL_MARGIN
    canvas_width = PFP_WIDTH

    for speech in data:
        speech_size = get_speech_size(speech)

        canvas_height += speech_size.height
        full_width = speech_size.width + TOTAL_MARGIN + PFP_WIDTH
        if full_width > canvas_width:
            canvas_width = full_width

    bg_raw = Image.open(f"{FILES_PATH}/bg.png").convert("RGBA")
    bg = bg_raw.resize((canvas_width, canvas_height))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0))
    canvas.paste(bg)

    speech_image_y = 0
    for speech in data:
        speech_size = get_speech_size(speech)
        speech_image = draw_speech(
            speech, Size(canvas_width, canvas_height), speech_image_y
        )

        canvas = Image.alpha_composite(canvas, speech_image)

        speech_image_y += speech_size.height

    canvas.save(name)
