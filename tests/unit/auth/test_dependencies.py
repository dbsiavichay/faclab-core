from types import SimpleNamespace

import pytest

from src.auth.domain.entities import AuthenticatedUser, Role
from src.auth.domain.exceptions import (
    InvalidTokenError,
    PasswordChangeRequiredError,
    PermissionDeniedError,
    TokenExpiredError,
)
from src.auth.domain.permissions import Permission
from src.auth.infra.dependencies import (
    get_current_user,
    get_optional_user,
    require_permission,
)


def _request(**state):
    return SimpleNamespace(state=SimpleNamespace(**state))


def _admin() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=1,
        username="admin",
        role=Role.ADMIN,
        permissions=frozenset({Permission.USER_MANAGE}),
    )


def test_get_optional_user_returns_none_when_missing():
    assert get_optional_user(_request(current_user=None)) is None


def test_get_optional_user_returns_user_when_present():
    user = _admin()
    assert get_optional_user(_request(current_user=user)) is user


def test_get_current_user_raises_permission_denied_when_no_header():
    with pytest.raises(PermissionDeniedError):
        get_current_user(_request(current_user=None, auth_error=None))


def test_get_current_user_raises_token_expired():
    with pytest.raises(TokenExpiredError):
        get_current_user(_request(current_user=None, auth_error="token_expired"))


def test_get_current_user_raises_invalid_token():
    with pytest.raises(InvalidTokenError):
        get_current_user(_request(current_user=None, auth_error="invalid_token"))


def test_get_current_user_returns_user():
    user = _admin()
    assert get_current_user(_request(current_user=user)) is user


def test_require_permission_allows_when_user_has_all():
    user = _admin()
    dep = require_permission(Permission.USER_MANAGE)
    assert dep(user=user) is user


def test_require_permission_raises_when_missing():
    user = AuthenticatedUser(
        id=2,
        username="viewer",
        role=Role.VIEWER,
        permissions=frozenset(),
    )
    dep = require_permission(Permission.USER_MANAGE)
    with pytest.raises(PermissionDeniedError):
        dep(user=user)


def test_require_permission_blocks_when_must_change_password():
    user = AuthenticatedUser(
        id=3,
        username="cashier",
        role=Role.CASHIER,
        permissions=frozenset({Permission.POS_OPERATE}),
        must_change_password=True,
    )
    dep = require_permission(Permission.POS_OPERATE)
    with pytest.raises(PasswordChangeRequiredError):
        dep(user=user)
