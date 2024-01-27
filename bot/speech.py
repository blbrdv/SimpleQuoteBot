from PIL import Image

from bot.avatar import generate_avatar
from bot.color import get_color
from bot.constants import TOTAL_MARGIN, MARGIN, PFP_WIDTH
from bot.message import draw_message, get_message_size
from bot.types.Point import Point
from bot.types.Size import Size
from bot.types.Speech import Speech


def get_speech_size(speech: Speech) -> Size:
    canvas_height = 0
    canvas_width = 0

    for index, message in enumerate(speech.messages):
        message_size = get_message_size(message, index == 0)

        canvas_height += message_size.height + TOTAL_MARGIN
        if message_size.width + TOTAL_MARGIN > canvas_width:
            canvas_width = message_size.width + TOTAL_MARGIN

    return Size(canvas_width, canvas_height)


def draw_speech(speech: Speech, canvas_size: Size, speech_image_y: int) -> Image:
    speech_size = get_speech_size(speech)
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), (0, 0, 0, 0))

    message_image_y = TOTAL_MARGIN + speech_image_y
    for index, message in enumerate(speech.messages):
        message_image = draw_message(
            message,
            canvas_size,
            message_image_y,
            get_color(speech.author.user_id).primary,
            index == 0,
        )

        canvas = Image.alpha_composite(canvas, message_image)

        message_size = get_message_size(message, index == 0)
        message_image_y += message_size.height + TOTAL_MARGIN

    pfp = generate_avatar(
        speech.author.initials,
        get_color(speech.author.user_id),
        Point(MARGIN, MARGIN + speech_image_y + speech_size.height - PFP_WIDTH),
        canvas_size,
    )
    canvas = Image.alpha_composite(canvas, pfp)

    return canvas
