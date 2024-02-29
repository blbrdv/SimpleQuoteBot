from typing import Optional

from PIL import Image, PyAccess

from bot.params import Params, Theme
from bot.speech import Speech
from bot.utils import open_file, full_path, fill_template


def draw(speeches: list[Speech], chrome_executable: Optional[str], file_name: str, params: Params) -> None:
    from html2image import Html2Image

    hti_params = {
        "size": (781, 4000),
        "custom_flags": [
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--headless=new",
            "--hide-scrollbars",
            "--log-level=3",
        ],
    }

    if chrome_executable:
        hti_params["browser_executable"] = "/opt/google/chrome/chrome"

    hti = Html2Image(**hti_params)

    content = ""
    for speech in speeches:
        content += speech.draw()

    html = fill_template(
        full_path("files/main.html"),
        content=content,
        prismstyle=full_path("files/prism.css"),
        prismscript=full_path("files/prism.js"),
    )

    css_fonts = fill_template(
        full_path("files/fonts.css"),
        fontregular=full_path("files/font_regular.ttf"),
        fontemoji=full_path("files/font_emoji.ttf"),
        fontmono=full_path("files/font_mono.ttf"),
    )
    if params.theme == Theme.LIGHT:
        css_bg = fill_template(
            full_path("files/theme.css"),
            path=full_path("files/bg_light.png"),
            bgcolor="white",
            color="black",
        )
    else:
        css_bg = fill_template(
            full_path("files/theme.css"),
            path=full_path("files/bg_dark.png"),
            bgcolor="#202123",
            color="white",
        )
    css_file = open_file("files/style.css")
    css = css_bg + css_fonts + css_file
    if params.is_anon:
        css_anon = open_file("files/anon.css")
        css += css_anon

    hti.screenshot(html_str=html, css_str=css, save_as=file_name)

    im = Image.open(file_name)
    pixels: PyAccess = im.load()
    width, height = im.size

    pixel = pixels[width - 1, 11]
    real_width = width - 1
    while pixel != (0, 0, 0, 255):
        real_width -= 1
        pixel = pixels[real_width, 11]

    pixel = pixels[60, height - 1]
    real_height = height - 1
    while pixel != (0, 0, 0, 255):
        if real_height == 0:
            real_height = height
            break

        real_height -= 1
        pixel = pixels[60, real_height]

    canvas = Image.new("RGBA", (real_width, real_height), (0, 0, 0, 0))
    canvas.paste(im)
    canvas.save(file_name)
