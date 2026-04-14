from enum import StrEnum

from src.auth.domain.entities import Role


class Permission(StrEnum):
    USER_MANAGE = "user:manage"


PERMISSIONS_BY_ROLE: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.MANAGER: frozenset(),
    Role.OPERATOR: frozenset(),
    Role.VIEWER: frozenset(),
}


def permissions_for(role: Role) -> frozenset[Permission]:
    return PERMISSIONS_BY_ROLE[role]
