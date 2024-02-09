from os import getenv
from string import Template

from PIL import Image, PyAccess

from bot.params import Params, Theme
from bot.speech import Speech
from bot.utils import open_file, full_path

MAIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple quotes</title>
</head>
<body>
    <div class="speeches">
        $content
    </div>
</body>
</html>"""
CSS_FONTS = """
@font-face {
    font-family: "Noto Sans";
    src: url("$fontregular");
}

@font-face {
    font-family: "Noto Mono";
    src: url("$fontmono");
}
"""
CSS_THEME = """
.speeches { 
  background: url("$path");
}

.message {
    background: $bgcolor;
    color: $color;
}

.tail > path {
    fill: $bgcolor;
}"""


def draw(speeches: list[Speech], name: str, params: Params) -> None:
    from html2image import Html2Image

    hti = Html2Image(
        size=(514, 4000),
        custom_flags=[
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--headless=new",
            "--hide-scrollbars",
            "--log-level=3",
        ],
    )
    html_template = Template(MAIN_HTML)

    content = ""
    for speech in speeches:
        content += speech.draw()

    html = html_template.substitute(content=content)

    css_font_template = Template(CSS_FONTS)
    css_fonts = css_font_template.substitute(
        fontregular=full_path("files/font_regular.ttf"),
        fontmono=full_path("files/font_mono.ttf"),
    )
    css_bg_template = Template(CSS_THEME)
    if params.theme == Theme.LIGHT:
        css_bg = css_bg_template.substitute(
            path=full_path("files/bg_light.png"), bgcolor="white", color="black"
        )
    else:
        css_bg = css_bg_template.substitute(
            path=full_path("files/bg_dark.png"), bgcolor="#202123", color="white"
        )
    css_file = open_file("files/style.css")
    css = css_bg + css_fonts + css_file
    if params.is_anon:
        css_anon = open_file("files/anon.css")
        css += css_anon

    hti.screenshot(html_str=html, css_str=css, save_as=name)

    im = Image.open(name)
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
    canvas.save(name)
