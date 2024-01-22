from typing import Optional

from .Author import Author
from .Message import Message


class Speech:
    """Multiple messages from one user in a row"""

    def __init__(self, author: Author, pfp: Optional[str], messages: list[Message]):
        self.author = author
        self.pfp = pfp
        self.messages = messages.copy()

    author: Author
    pfp: Optional[str]
    messages: list[Message]
