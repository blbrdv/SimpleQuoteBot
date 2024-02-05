from string import Template

from bot.color import get_color
from bot.message import IncomingMessage

SPEECH_HTML = """
<div class="speech">
    $avatar
    <svg class="tail">
        <path d="M 0,15 15,15 15,0 M 15,0 C 15,4 4,15 0,15" />
    </svg>
    <div class="messages">
        $content
    </div>
</div>"""


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

    def draw(self) -> str:
        str_template = Template(SPEECH_HTML)

        content = ""
        for message in self.messages:
            content += message.draw()

        return str_template.substitute(content=content, avatar=self.pfp)
