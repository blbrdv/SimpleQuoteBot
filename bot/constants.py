import os

from PIL import ImageFont

TEXT_FONT_SIZE = 20
TIME_FONT_SIZE = 15
INITIALS_FONT_SIZE = 32
FILES_PATH = f"{os.getcwd()}/files"
TEXT_REG_FONT = ImageFont.truetype(f"{FILES_PATH}/font_regular.ttf", TEXT_FONT_SIZE)
TEXT_IT_FONT = ImageFont.truetype(f"{FILES_PATH}/font_italic.ttf", TEXT_FONT_SIZE)
TEXT_BLD_FONT = ImageFont.truetype(f"{FILES_PATH}/font_bold.ttf", TEXT_FONT_SIZE)
TEXT_BLD_IT_FONT = ImageFont.truetype(
    f"{FILES_PATH}/font_bold_italic.ttf", TEXT_FONT_SIZE
)
TEXT_MONO_FONT = ImageFont.truetype(f"{FILES_PATH}/font_mono.ttf", TEXT_FONT_SIZE)
MARGIN = 12
TOTAL_MARGIN = MARGIN * 2
PFP_WIDTH = 75
