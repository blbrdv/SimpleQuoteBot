import os

from PIL import ImageFont

RGBA_ZERO = (0, 0, 0, 0)
TEXT_FONT_SIZE = 20
FILES_PATH = f"{os.getcwd()}/files"
TEXT_REG_FONT = ImageFont.truetype(f"{FILES_PATH}/font_regular.ttf", TEXT_FONT_SIZE)
MARGIN = 12
TOTAL_MARGIN = MARGIN * 2
PFP_WIDTH = 75
