from typing import Optional

from Author import Author


class Message:
    """Single message record"""

    def __init__(
        self, text: str, *, last: bool = False, author: Optional[Author] = None
    ):
        self.text = text
        self.last = last
        self.author = author

    text: str
    last: bool
    author: Optional[Author]

    @property
    def is_first(self) -> bool:
        return bool(self.author)

    @property
    def is_last(self) -> bool:
        return self.last
