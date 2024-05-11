import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Tuple, Optional
from xml.etree import ElementTree as ET

import xxhash
from aiogram.enums import MessageOriginType, ContentType
from aiogram.types import Message

from bot.color import get_color
from bot.utils import full_path, fill_template


class IncomingMessage(ABC):
    author_id: int
    message_id: int
    pfp: str
    initials: str
    media_group_count: int = 0
    full_name: str
    text_for_reply: str
    image: str
    photo: Optional[str] = None

    @staticmethod
    async def _download_file(message: Message, file_id: str) -> str:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        file_name = f"temp/{file_id}.png"

        file_path = await message.bot.get_file(file_id)
        await message.bot.download_file(file_path.file_path, file_name)

        return file_name

    @staticmethod
    async def _get_avatar(message: Message, user_id: int) -> Optional[str]:
        pfps = await message.bot.get_user_profile_photos(user_id, limit=1)
        pfp: Optional[str] = None

        if pfps.total_count > 0:
            file_name = await Bubble._download_file(message, pfps.photos[0][0].file_id)
            pfp = (
                f"""<img class="avatar" src="{full_path(file_name)}" alt="avatar" />"""
            )

        return pfp

    @abstractmethod
    def draw(self) -> str:
        pass


class Bubble(IncomingMessage):
    message_id: int
    author_id: int
    first_name: str
    last_name: Optional[str] = None
    full_name: str
    initials: str
    text: str
    text_for_reply: str
    photo: Optional[str] = None
    media_group_count: int = 0
    reply: Optional[IncomingMessage] = None
    time: str
    pfp: Optional[str] = None
    is_first: bool = False
    unsupported_type: bool = False

    @classmethod
    def from_incoming_message(cls, message: IncomingMessage) -> "Bubble":
        self = cls()

        self.message_id = message.message_id
        self.author_id = message.author_id
        self.initials = message.initials
        self.media_group_count = message.media_group_count
        self.pfp = message.pfp
        self.full_name = message.full_name
        self.text_for_reply = message.text_for_reply
        self.photo = message.photo

        return self

    @classmethod
    async def create(cls, message: Message) -> "Bubble":
        self = cls()
        (
            self.message_id,
            self.author_id,
            self.first_name,
            self.last_name,
            text,
            self.time,
            self.pfp,
        ) = await Bubble._get_data(message)

        (self.text, self.text_for_reply) = Bubble._set_languages(text)

        full_name = self.first_name
        if self.last_name:
            full_name += f" {self.last_name}"
        self.full_name = full_name

        initials = self.first_name[0]
        if self.last_name:
            initials += self.last_name[0]
        self.initials = initials

        # no match cuz python version in docker < 3.10
        if message.content_type == ContentType.TEXT:
            pass
        elif message.content_type == ContentType.PHOTO:
            file_name = await Bubble._download_file(message, message.photo[-1].file_id)
            self.photo = full_path(file_name)
        else:
            self.unsupported_type = True

        return self

    @staticmethod
    async def _get_data(
        message: Message,
    ) -> Tuple[int, int, str, Optional[str], str, str, str]:
        message_id: int
        user_id: int
        first_name: str
        last_name: Optional[str] = None
        message_datetime: datetime
        pfp: Optional[str] = None

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
                if message.forward_origin.type == MessageOriginType.CHANNEL:
                    user_id = message.forward_origin.chat.id
                    first_name = message.forward_origin.chat.full_name
                elif message.forward_origin.type == MessageOriginType.CHAT:
                    user_id = message.forward_from_chat.id
                    name = message.forward_from_chat.full_name.split()
                    first_name = name[0]
                    if name[1:] is not None and name[1:] != "":
                        last_name = " ".join(name[1:])

                    # TODO: chat pfp
                else:
                    user_id = message.forward_origin.sender_user.id
                    first_name = message.forward_origin.sender_user.first_name
                    if (
                        message.forward_origin.sender_user.last_name is not None
                        and message.forward_origin.sender_user.last_name != ""
                    ):
                        last_name = message.forward_origin.sender_user.last_name

                    pfp = await Bubble._get_avatar(message, user_id)

            message_id = message.message_id
            message_datetime = message.forward_origin.date
        else:
            message_id = message.message_id
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            if (
                message.from_user.last_name is not None
                and message.from_user.last_name != ""
            ):
                last_name = message.from_user.last_name
            message_datetime = message.date

            pfp = await Bubble._get_avatar(message, user_id)

        return (
            message_id,
            user_id,
            first_name,
            last_name,
            message.html_text,
            message_datetime.replace(tzinfo=timezone.utc).strftime("%H:%M"),
            pfp,
        )

    @staticmethod
    def _set_languages(text: str) -> Tuple[str, str]:
        root = ET.fromstring(f"<root>{text}</root>")
        reply_text = ET.tostring(root, encoding="unicode", method="text")

        for pre in root.findall("pre"):
            code = pre.find("code")

            lang = code.attrib.get("class").replace("language-", "").replace("-", " ")
            language_name = ET.Element("p")
            language_name.text = lang

            pre.insert(0, language_name)

        return ET.tostring(root, encoding="unicode")[6:-7], reply_text

    def draw(self) -> str:
        header = ""
        if self.is_first:
            header = f"""<header style="color: {get_color(self.author_id).primary.hex};">{self.full_name}</header>"""

        reply = ""
        if self.reply:
            if type(self.reply) is Sticker:
                sticker = Sticker.from_incoming_message(self.reply)
                image = f"""<img class="preview" src="{sticker.image}" />"""
                color = get_color(sticker.author_id).primary
                reply = fill_template(
                    full_path("files/reply.html"),
                    image=image,
                    header=sticker.full_name,
                    content=sticker.text_for_reply,
                    color=color.hex,
                    colortext="black",
                    r=color.red,
                    g=color.green,
                    b=color.blue,
                )
            else:
                bubble = Bubble.from_incoming_message(self.reply)
                color = get_color(bubble.author_id).primary
                content = bubble.text_for_reply
                image = ""
                if bubble.photo:
                    image = f"""<img class="preview" src="{bubble.photo}" />"""
                    if content == "":
                        content = "Photo"

                reply = fill_template(
                    full_path("files/reply.html"),
                    image=image,
                    header=bubble.full_name,
                    content=content,
                    color=color.hex,
                    colortext="black",
                    r=color.red,
                    g=color.green,
                    b=color.blue,
                )

        additional = ""
        if self.photo:
            additional = f"""<img class="photo" src="{self.photo}" />"""
        elif self.unsupported_type:
            additional = f"""<div class="warning">❌ Unsupported message type</div>"""

        mediagroup = ""
        if self.media_group_count > 0:
            mediagroup = (
                f"""<div class="mediagroup">+{self.media_group_count} photo</div>"""
            )

        return fill_template(
            full_path("files/message.html"),
            header=header,
            additional=additional,
            mediagroup=mediagroup,
            reply=reply,
            content=self.text,
            time=self.time,
        )


class Sticker(IncomingMessage):
    author_id: int
    message_id: int
    full_name: str
    image: str
    reply: Optional[IncomingMessage] = None
    pfp: str
    initials: str
    media_group_count: int = 0

    @classmethod
    def from_incoming_message(cls, message: IncomingMessage) -> "Sticker":
        self = cls()

        self.author_id = message.author_id
        self.message_id = message.message_id
        self.initials = message.initials
        self.media_group_count = message.media_group_count
        self.pfp = message.pfp
        self.full_name = message.full_name
        self.text_for_reply = message.text_for_reply
        self.image = message.image

        return self

    @classmethod
    async def create(cls, message: Message) -> "Sticker":
        self = cls()

        author_id: id
        full_name: str
        pfp = ""
        initials: str
        if message.forward_origin:
            author_id = message.forward_origin.sender_user.id
            full_name = message.forward_origin.sender_user.full_name
            initials = message.forward_origin.sender_user.first_name[0]
            if message.forward_origin.sender_user.last_name:
                initials += message.forward_origin.sender_user.last_name[0]

            if message.forward_origin.type != MessageOriginType.HIDDEN_USER:
                pfp = await Bubble._get_avatar(message, author_id)
        else:
            author_id = message.from_user.id
            full_name = message.from_user.full_name
            pfp = await IncomingMessage._get_avatar(message, author_id)

            initials = message.from_user.first_name[0]
            if message.from_user.last_name:
                initials += message.from_user.last_name[0]
        self.author_id = author_id
        self.full_name = full_name
        self.pfp = pfp
        self.initials = initials
        self.message_id = message.message_id
        self.text_for_reply = f"{message.sticker.emoji} Sticker"

        file_name = await Sticker._download_file(message, message.sticker.file_id)
        self.image = full_path(file_name)

        return self

    def draw(self) -> str:
        reply = ""
        if self.reply:
            if type(self.reply) is Sticker:
                sticker = Sticker.from_incoming_message(self.reply)
                image = f"""<img class="preview" src="{sticker.image}" />"""
                reply = fill_template(
                    full_path("files/reply.html"),
                    image=image,
                    header=sticker.full_name,
                    content=sticker.text_for_reply,
                    color="white",
                    colortext="white",
                    r="255",
                    g="255",
                    b="255",
                )
            else:
                bubble = Bubble.from_incoming_message(self.reply)
                content = bubble.text_for_reply
                image = ""
                if bubble.photo:
                    image = f"""<img class="preview" src="{bubble.photo}" />"""
                    if content == "":
                        content = "Photo"

                reply = fill_template(
                    full_path("files/reply.html"),
                    image=image,
                    header=bubble.full_name,
                    content=content,
                    color="white",
                    colortext="white",
                    r="255",
                    g="255",
                    b="255",
                )

        return fill_template(
            full_path("files/sticker.html"),
            sticker=self.image,
            reply=reply,
        )
