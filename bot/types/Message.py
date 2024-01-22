from typing import Optional

import datetime as datetime


class Message:
    """Single message record"""

    def __init__(
        self,
        text: str,
        dt: datetime,
        *,
        last: bool = False,
        header: Optional[str] = None
    ):
        self.text = text
        self.time = dt.astimezone(datetime.timezone.utc).strftime("%H:%M")
        self.last = last
        self.header = header

    text: str
    time: str
    last: bool
    header: Optional[str]

    @property
    def is_first(self) -> bool:
        return bool(self.header)

    @property
    def is_last(self) -> bool:
        return self.last
