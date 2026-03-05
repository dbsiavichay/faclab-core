import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.exc import IntegrityError

from src.shared.infra.middlewares import ErrorHandlingMiddleware


def _make_middleware():
    app = MagicMock()
    return ErrorHandlingMiddleware(app)


def _make_request():
    req = MagicMock()
    req.headers = {}
    req.state = MagicMock()
    return req


def test_integrity_error_returns_409():
    middleware = _make_middleware()
    fake_request = _make_request()
    call_next = AsyncMock(
        side_effect=IntegrityError(
            statement="DELETE FROM units_of_measure WHERE id = 8",
            params={"id": 8},
            orig=Exception(
                'update or delete on table "units_of_measure" violates foreign key '
                'constraint "products_unit_of_measure_id_fkey" on table "products"'
            ),
        )
    )

    response = asyncio.get_event_loop().run_until_complete(
        middleware.dispatch(fake_request, call_next)
    )

    assert response.status_code == 409
    body = json.loads(response.body)
    assert body["errors"][0]["code"] == "INTEGRITY_ERROR"
    assert "referenced by other records" in body["errors"][0]["message"]
    assert "requestId" in body["meta"]
    assert "timestamp" in body["meta"]
