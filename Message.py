from datetime import timezone

from aiogram.types import DateTime


class Message:
    """Single message record"""

    def __init__(self, text: str, datetime: DateTime):
        self.text = text
        self.time = datetime.replace(tzinfo=timezone.utc).strftime("%H:%M")

    text: str
    time: str
