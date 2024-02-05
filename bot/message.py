import os
from datetime import datetime, timezone
from string import Template
from typing import Tuple

import xxhash
from aiogram.enums import MessageOriginType
from aiogram.types import Message

from bot.color import get_color
from bot.utils import full_path

MESSAGE_HTML = """
<div class="message">
    <div class="content">
        $header$reply<p>$content</p>
    </div>
    <div class="time">$time</div>
</div>"""
REPLY_HTML = """
<div class="reply" style="border-left: 5px solid $color; background: rgba($r, $g, $b, 0.1);">
    <header style="color: $color;">$header</header>
    <p>$content</p>
</div>"""


class IncomingMessage(object):
    @classmethod
    async def create(cls, message: Message, is_first: bool = False):
        self = cls()
        (
            self.author_id,
            self.first_name,
            self.last_name,
            self.text,
            self.time,
            self.pfp,
        ) = await IncomingMessage._get_data(message)
        self.is_first = is_first

        if message.reply_to_message:
            (
                self.reply_author_id,
                first_name,
                last_name,
                self.reply_text,
                _,
                _,
            ) = await IncomingMessage._get_data(message.reply_to_message)

            if last_name:
                self.reply_author_name = f"{first_name} {last_name}"
            else:
                self.reply_author_name = first_name

        full_name = self.first_name
        if self.last_name:
            full_name += f" {self.last_name}"
        self.full_name = full_name

        initials = self.first_name[0]
        if self.last_name:
            initials += self.last_name[0]
        self.initials = initials

        return self

    author_id: int
    first_name: str
    last_name: str | None = None
    full_name: str
    initials: str
    text: str
    reply_text: str | None = None
    reply_author_id: int | None = None
    reply_author_name: str | None = None
    time: str
    pfp: str | None = None
    is_first: bool = False

    @staticmethod
    async def _get_avatar(message: Message, user_id: int) -> str | None:
        pfps = await message.bot.get_user_profile_photos(user_id, limit=1)
        pfp: str | None = None

        if pfps.total_count > 0:
            if not os.path.exists("temp"):
                os.makedirs("temp")
            file_name = f"temp/{user_id}.png"

            pfp_file = await message.bot.get_file(pfps.photos[0][0].file_id)
            await message.bot.download_file(pfp_file.file_path, file_name)
            pfp = f"""<img class="avatar" src="{full_path(file_name)}" alt="avatar"/>"""

        return pfp

    @staticmethod
    async def _get_data(
        message: Message,
    ) -> Tuple[int, str, str | None, str, str, str]:
        user_id: int
        first_name: str
        last_name: str | None = None
        message_datetime: datetime
        pfp: str | None = None

        if message.forward_origin:
            if message.forward_origin.type == MessageOriginType.HIDDEN_USER:
                # hidden user doesn't provide id :^(
                user_id = xxhash.xxh32_intdigest(
                    message.forward_origin.sender_user_name
                )
                name = message.forward_origin.sender_user_name.split()
                first_name = name[0]
                if name[1:] is not None and name[1:] != "":
                    last_name = " ".join(name[1:])
            else:
                user_id = message.forward_origin.sender_user.id
                first_name = message.forward_origin.sender_user.first_name
                if (
                    message.forward_origin.sender_user.last_name is not None
                    and message.forward_origin.sender_user.last_name != ""
                ):
                    last_name = message.forward_origin.sender_user.last_name

                pfp = await IncomingMessage._get_avatar(message, user_id)

            message_datetime = message.forward_origin.date
        else:
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            if (
                message.from_user.last_name is not None
                and message.from_user.last_name != ""
            ):
                last_name = message.from_user.last_name
            message_datetime = message.date

            pfp = await IncomingMessage._get_avatar(message, user_id)

        return (
            user_id,
            first_name,
            last_name,
            message.html_text,
            message_datetime.replace(tzinfo=timezone.utc).strftime("%H:%M"),
            pfp,
        )

    def draw(self) -> str:
        str_template = Template(MESSAGE_HTML)

        header = ""
        if self.is_first:
            header = f"""<header style="color: {get_color(self.author_id).primary.hex};">{self.full_name}</header>"""

        reply = ""
        if self.reply_text:
            color=get_color(self.reply_author_id).primary
            reply_template = Template(REPLY_HTML)
            reply = reply_template.substitute(
                header=self.reply_author_name,
                content=self.reply_text,
                color=color.hex,
                r=color.red,
                g=color.green,
                b=color.blue,
            )

        return str_template.substitute(
            header=header, reply=reply, content=self.text, time=self.time
        )
