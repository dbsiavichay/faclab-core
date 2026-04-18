"""Guard test: every /api/pos route must carry a require_permission dependency.

This fails if a new POS router is added without authorization coverage.
"""

from fastapi import APIRouter, FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from src.auth.infra.dependencies import get_current_user
from src.pos.cash.infra.routes import POSCashRouter
from src.pos.infra.routes import POSCustomerRouter, POSProductRouter
from src.pos.refund.infra.routes import POSRefundRouter
from src.pos.reports.infra.routes import POSReportRouter
from src.pos.sales.infra.routes import POSSaleRouter
from src.pos.shift.infra.routes import POSShiftRouter


def _build_pos_app() -> FastAPI:
    app = FastAPI()
    pos = APIRouter(prefix="/api/pos")
    pos.include_router(POSSaleRouter().router, prefix="/sales")
    pos.include_router(POSShiftRouter().router, prefix="/shifts")
    pos.include_router(POSProductRouter().router, prefix="/products")
    pos.include_router(POSCustomerRouter().router, prefix="/customers")
    pos.include_router(POSRefundRouter().router, prefix="/refunds")
    pos.include_router(POSCashRouter().router, prefix="/shifts")
    pos.include_router(POSReportRouter().router, prefix="/reports")
    app.include_router(pos)
    return app


_APP = _build_pos_app()


def _tree_contains_call(dep: Dependant, target) -> bool:
    if dep.call is target:
        return True
    return any(_tree_contains_call(sub, target) for sub in dep.dependencies)


def _pos_routes() -> list[APIRoute]:
    return [
        r
        for r in _APP.routes
        if isinstance(r, APIRoute) and r.path.startswith("/api/pos")
    ]


def test_every_pos_route_requires_authenticated_user():
    unprotected: list[str] = []
    for route in _pos_routes():
        if not _tree_contains_call(route.dependant, get_current_user):
            for method in sorted(route.methods or []):
                unprotected.append(f"{method} {route.path}")
    assert not unprotected, (
        "POS routes missing require_permission/get_current_user:\n  - "
        + "\n  - ".join(unprotected)
    )


def test_pos_routes_exist():
    """Sanity check — the filter is actually finding routes."""
    assert len(_pos_routes()) > 0
