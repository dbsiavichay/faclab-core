from src.auth.domain.entities import Role
from src.auth.domain.permissions import Permission, permissions_for


def test_admin_has_all_permissions():
    assert permissions_for(Role.ADMIN) == frozenset(Permission)


def test_manager_has_everything_but_user_manage_and_pos_operate():
    perms = permissions_for(Role.MANAGER)
    assert Permission.USER_MANAGE not in perms
    assert Permission.POS_OPERATE not in perms
    assert Permission.SALE_CANCEL in perms
    assert Permission.PURCHASE_CONFIRM in perms
    assert Permission.PURCHASE_RECEIVE in perms
    assert Permission.REFUND_APPROVE in perms


def test_operator_has_back_office_writes_but_not_critical_ops():
    perms = permissions_for(Role.OPERATOR)
    assert Permission.PRODUCT_WRITE in perms
    assert Permission.MOVEMENT_WRITE in perms
    assert Permission.ADJUSTMENT_WRITE in perms
    assert Permission.PURCHASE_WRITE in perms
    assert Permission.SALE_WRITE in perms
    assert Permission.SALE_CANCEL not in perms
    assert Permission.PURCHASE_CONFIRM not in perms
    assert Permission.REFUND_APPROVE not in perms
    assert Permission.POS_OPERATE not in perms
    assert Permission.USER_MANAGE not in perms


def test_viewer_only_has_reads():
    perms = permissions_for(Role.VIEWER)
    for p in perms:
        assert p.value.endswith(":read"), f"viewer should only have reads, got {p}"
    assert Permission.PRODUCT_READ in perms
    assert Permission.SALE_READ in perms
    assert Permission.REPORT_INVENTORY_READ in perms
    assert Permission.REPORT_POS_READ in perms
    assert Permission.PRODUCT_WRITE not in perms


def test_cashier_can_operate_pos_but_not_admin():
    perms = permissions_for(Role.CASHIER)
    assert Permission.POS_OPERATE in perms
    assert Permission.SALE_WRITE in perms
    assert Permission.CUSTOMER_WRITE in perms
    assert Permission.REPORT_POS_READ in perms
    assert Permission.USER_MANAGE not in perms
    assert Permission.PURCHASE_WRITE not in perms
    assert Permission.MOVEMENT_WRITE not in perms
    assert Permission.SALE_CANCEL not in perms


def test_viewer_cannot_write_products():
    assert Permission.PRODUCT_WRITE not in permissions_for(Role.VIEWER)


def test_operator_cannot_cancel_sales():
    assert Permission.SALE_CANCEL not in permissions_for(Role.OPERATOR)


def test_manager_cannot_manage_users():
    assert Permission.USER_MANAGE not in permissions_for(Role.MANAGER)
