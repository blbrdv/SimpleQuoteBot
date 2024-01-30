from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

from bot.constants import (
    TEXT_REG_FONT,
    MARGIN,
    TOTAL_MARGIN,
    PFP_WIDTH,
    TEXT_FONT_SIZE,
    RGBA_ZERO,
    FILES_PATH,
)
from bot.text import get_text_size, draw_md_text, draw_reply, get_reply_width
from bot.types.Message import Message
from bot.types.Point import Point
from bot.types.RGB import RGB
from bot.types.Size import Size

TIME_FONT_SIZE = 16
TIME_FONT = ImageFont.truetype(f"{FILES_PATH}/font_regular.ttf", TIME_FONT_SIZE)


def get_message_size(message: Message, is_first: bool) -> Size:
    text_size = get_text_size(message.text, TEXT_REG_FONT)
    time_size = get_text_size(message.time, TEXT_REG_FONT)

    width = text_size.width + TOTAL_MARGIN + TOTAL_MARGIN + time_size.width + MARGIN
    height = text_size.height + int(time_size.height / 2)

    if not is_first:
        height += MARGIN

    if message.reply_text:
        height += TEXT_FONT_SIZE * 2 + MARGIN * 3

    if message.is_first:
        user_name_size = get_text_size(message.header, TEXT_REG_FONT)
        user_name_width = user_name_size.width + TOTAL_MARGIN + TOTAL_MARGIN

        if user_name_width > width:
            width = user_name_width
        height += user_name_size.height + TOTAL_MARGIN

    return Size(width, height)


def draw_message(
    message: Message, canvas_size: Size, y: int, header_color: RGB, is_first: bool
) -> Image:
    message_size = get_message_size(message, is_first)
    text_size = get_text_size(message.text, TEXT_REG_FONT)
    canvas = Image.new("RGBA", (canvas_size.width, canvas_size.height), RGBA_ZERO)
    d = ImageDraw.Draw(canvas)
    pij = Pilmoji(canvas)

    rectangle_y = y + message_size.height + MARGIN

    width = message_size.width
    if message.reply:
        reply_width = get_reply_width(message.reply.fullname, message.reply.text) + TOTAL_MARGIN * 2
        if reply_width > message_size.width:
            width = reply_width
    width += TOTAL_MARGIN + PFP_WIDTH

    d.rounded_rectangle(
        (
            TOTAL_MARGIN * 2 + PFP_WIDTH,
            y,
            width,
            rectangle_y,
        ),
        radius=5,
        fill="#202123",
        corners=(True, True, True, not message.is_last),
    )
    if message.is_last:
        d.polygon(
            [
                (TOTAL_MARGIN * 2 + PFP_WIDTH, rectangle_y),
                (TOTAL_MARGIN * 2 + PFP_WIDTH, rectangle_y - 8),
                (TOTAL_MARGIN * 2 + PFP_WIDTH - 10, rectangle_y),
            ],
            fill="#202123",
        )

    text_y = y + MARGIN

    if message.is_first:
        pij.text(
            (TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, y + MARGIN),
            message.header,
            fill=header_color.value,
            font=TEXT_REG_FONT,
        )
        text_y += TEXT_FONT_SIZE + MARGIN

    time_y = rectangle_y - TOTAL_MARGIN - int(TIME_FONT_SIZE / 2)
    if message.reply:
        time_y += MARGIN
    d.text(
        (
            TOTAL_MARGIN * 2 + MARGIN * 2 + PFP_WIDTH + text_size.width,
            time_y,
        ),
        message.time,
        fill="grey",
        font=TIME_FONT,
    )

    if message.reply:
        reply = draw_reply(
            message.reply.fullname,
            message.reply.text,
            canvas_size,
            Point(TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, text_y),
            header_color.value,
        )
        canvas = Image.alpha_composite(canvas, reply)

        text_y += TEXT_FONT_SIZE * 4 + MARGIN

    text_image = draw_md_text(
        message.text,
        TEXT_FONT_SIZE,
        Point(TOTAL_MARGIN * 2 + MARGIN + PFP_WIDTH, text_y),
        canvas_size,
    )
    canvas = Image.alpha_composite(canvas, text_image)

    return canvas
