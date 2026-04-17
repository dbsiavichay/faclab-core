from enum import StrEnum

from src.auth.domain.entities import Role


class Permission(StrEnum):
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    STOCK_READ = "stock:read"
    MOVEMENT_WRITE = "movement:write"
    SALE_READ = "sale:read"
    SALE_WRITE = "sale:write"
    SALE_CANCEL = "sale:cancel"
    USER_MANAGE = "user:manage"


PERMISSIONS_BY_ROLE: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.MANAGER: frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.PRODUCT_WRITE,
            Permission.STOCK_READ,
            Permission.MOVEMENT_WRITE,
            Permission.SALE_READ,
            Permission.SALE_WRITE,
            Permission.SALE_CANCEL,
        }
    ),
    Role.OPERATOR: frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.STOCK_READ,
            Permission.SALE_READ,
            Permission.SALE_WRITE,
        }
    ),
    Role.VIEWER: frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.STOCK_READ,
            Permission.SALE_READ,
        }
    ),
}


def permissions_for(role: Role) -> frozenset[Permission]:
    return PERMISSIONS_BY_ROLE[role]
