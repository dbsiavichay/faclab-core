from src.auth.domain.entities import Role
from src.auth.domain.permissions import Permission, permissions_for


def test_admin_has_all_permissions():
    assert permissions_for(Role.ADMIN) == frozenset(Permission)


def test_manager_permissions():
    expected = frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.PRODUCT_WRITE,
            Permission.STOCK_READ,
            Permission.MOVEMENT_WRITE,
            Permission.SALE_READ,
            Permission.SALE_WRITE,
            Permission.SALE_CANCEL,
        }
    )
    assert permissions_for(Role.MANAGER) == expected


def test_operator_permissions():
    expected = frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.STOCK_READ,
            Permission.SALE_READ,
            Permission.SALE_WRITE,
        }
    )
    assert permissions_for(Role.OPERATOR) == expected


def test_viewer_permissions():
    expected = frozenset(
        {
            Permission.PRODUCT_READ,
            Permission.STOCK_READ,
            Permission.SALE_READ,
        }
    )
    assert permissions_for(Role.VIEWER) == expected


def test_viewer_cannot_write_products():
    assert Permission.PRODUCT_WRITE not in permissions_for(Role.VIEWER)


def test_operator_cannot_cancel_sales():
    assert Permission.SALE_CANCEL not in permissions_for(Role.OPERATOR)


def test_manager_cannot_manage_users():
    assert Permission.USER_MANAGE not in permissions_for(Role.MANAGER)
