from dataclasses import dataclass
from typing import Any

from src.shared.domain.events import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    user_id: int = 0
    username: str = ""
    email: str = ""
    role: int = 0

    def _payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
        }
