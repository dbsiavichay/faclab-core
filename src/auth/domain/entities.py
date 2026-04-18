from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum

from src.shared.domain.entities import Entity


class Role(IntEnum):
    ADMIN = 1
    MANAGER = 2
    OPERATOR = 3
    VIEWER = 4
    CASHIER = 5


@dataclass
class User(Entity):
    username: str
    email: str
    password_hash: str
    role: Role = Role.VIEWER
    id: int | None = None
    is_active: bool = True
    last_login_at: datetime | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: Role
    permissions: frozenset = field(default_factory=frozenset)
