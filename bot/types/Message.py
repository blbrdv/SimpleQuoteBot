import textwrap
from typing import Optional

import datetime as datetime
from aiogram.types import Message as Msg

from bot.types.Reply import Reply


class Message:
    """Single message record"""

    def __init__(
        self,
        message: Msg,
        text: str,
        reply_text: str,
        dt: datetime,
        *,
        last: bool = False,
        header: Optional[str] = None
    ):
        self.text = "\n".join(textwrap.TextWrapper(width=50).wrap(text=text))

        _reply_text = reply_text.replace("\\n", "")
        if len(reply_text) > 15:
            _reply_text = textwrap.TextWrapper(width=15).wrap(_reply_text)[0]
        self.reply_text = _reply_text

        self.time = dt.astimezone(datetime.timezone.utc).strftime("%H:%M")
        self.last = last
        self.header = header

        if message.reply_to_message:
            self.reply = Reply(message.reply_to_message)

    text: str
    reply_text: Optional[str]
    time: str
    last: bool
    header: Optional[str]
    reply: Optional[Reply] = None

    @property
    def is_first(self) -> bool:
        return bool(self.header)

    @property
    def is_last(self) -> bool:
        return self.last
