from Message import Message


class Speech:
    """Multiple messages from one user in a row"""

    def __init__(self, author_name: str, author_avatar: str, messages: list[Message]):
        self.author_name = author_name
        self.author_avatar = author_avatar
        self.messages = messages.copy()

    author_name: str
    author_avatar: str
    messages: list[Message]
