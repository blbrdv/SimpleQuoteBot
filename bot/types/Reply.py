import textwrap

import xxhash
from aiogram.enums import MessageOriginType
from aiogram.types import Message


class Reply:
    def __init__(self, message: Message):
        user_id = 0
        fullname = ""
        if message.forward_origin:
            if message.forward_origin.type == MessageOriginType.HIDDEN_USER:
                # hidden user doesn't provide id :^(
                user_id = xxhash.xxh32_intdigest(
                    message.forward_origin.sender_user_name
                )
                fullname = message.forward_origin.sender_user_name
            else:
                user_id = message.forward_origin.sender_user.id
                fullname = message.forward_origin.sender_user.full_name
        else:
            user_id = message.from_user.id
            fullname = message.from_user.full_name

        self.id = user_id
        self.fullname = fullname

        _reply_text = message.md_text.replace("\\n", "")
        if len(message.md_text) > 15:
            _reply_text = textwrap.TextWrapper(width=15).wrap(_reply_text)[0]
        self.text = _reply_text

    id: int
    fullname: str
    text: str
