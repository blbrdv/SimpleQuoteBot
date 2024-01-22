from typing import Optional


class Author:
    def __init__(self, user_id: int, first_name: str, last_name: Optional[str] = None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name

    user_id: int
    first_name: str
    last_name: Optional[str]

    @property
    def full_name(self) -> str:
        result = self.first_name

        if self.last_name:
            result += f" {self.last_name}"

        return result

    @property
    def initials(self) -> str:
        result = self.first_name[0]

        if self.last_name:
            result += self.last_name[0]

        return result
