from bot.color import get_color
from bot.message import IncomingMessage, Sticker
from bot.utils import full_path, fill_template


class Speech:
    def __init__(self, messages: list[IncomingMessage]):
        self.messages = messages.copy()

        if len(messages) > 0:
            first_message = self.messages[0]
            first_message.is_first = True
            pfp = first_message.pfp

            if not pfp:
                color = get_color(first_message.author_id)
                pfp = f"""<div class="avatar" style="background-image: linear-gradient({color.secondary.hex}, {color.primary.hex})">
                    {first_message.initials}
                </div>"""

            self.pfp = pfp

    pfp: str
    messages: list[IncomingMessage]
    visibility: str = "visible"

    def draw(self) -> str:
        content = ""
        for message in self.messages:
            content += message.draw()

        if type(self.messages[-1]) is Sticker:
            self.visibility = "hidden"

        return fill_template(full_path("files/speech.html"), content=content, avatar=self.pfp, visibility=self.visibility)
