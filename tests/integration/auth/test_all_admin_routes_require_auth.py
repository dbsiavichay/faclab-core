"""Guard test: every /api/admin route must carry a require_permission dependency.

This fails if a new admin router is added without authorization coverage.
"""

from fastapi import APIRouter, FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from src.auth.infra.admin_routes import UserAdminRouter
from src.auth.infra.dependencies import get_current_user
from src.catalog.product.infra.routes import CategoryRouter, ProductRouter
from src.catalog.uom.infra.routes import UnitOfMeasureRouter
from src.customers.infra.routes import CustomerContactRouter, CustomerRouter
from src.inventory.adjustment.infra.routes import AdjustmentItemRouter, AdjustmentRouter
from src.inventory.alert.infra.routes import AlertRouter
from src.inventory.location.infra.routes import LocationRouter
from src.inventory.lot.infra.routes import LotRouter
from src.inventory.movement.infra.routes import MovementRouter
from src.inventory.serial.infra.routes import SerialRouter
from src.inventory.stock.infra.routes import StockRouter
from src.inventory.transfer.infra.routes import TransferItemRouter, TransferRouter
from src.inventory.warehouse.infra.routes import WarehouseRouter
from src.purchasing.infra.routes import POItemRouter, PurchaseOrderRouter
from src.reports.inventory.infra.routes import ReportRouter
from src.sales.infra.routes import SaleRouter
from src.suppliers.infra.routes import (
    SupplierContactRouter,
    SupplierProductRouter,
    SupplierRouter,
)


def _build_admin_app() -> FastAPI:
    app = FastAPI()
    admin = APIRouter(prefix="/api/admin")
    admin.include_router(CategoryRouter().router, prefix="/categories")
    admin.include_router(UnitOfMeasureRouter().router, prefix="/units-of-measure")
    admin.include_router(ProductRouter().router, prefix="/products")
    admin.include_router(WarehouseRouter().router, prefix="/warehouses")
    admin.include_router(LocationRouter().router, prefix="/locations")
    admin.include_router(StockRouter().router, prefix="/stock")
    admin.include_router(MovementRouter().router, prefix="/movements")
    admin.include_router(LotRouter().router, prefix="/lots")
    admin.include_router(SerialRouter().router, prefix="/serials")
    admin.include_router(CustomerRouter().router, prefix="/customers")
    admin.include_router(CustomerContactRouter().router, prefix="/customer-contacts")
    admin.include_router(SupplierRouter().router, prefix="/suppliers")
    admin.include_router(SupplierContactRouter().router, prefix="/supplier-contacts")
    admin.include_router(SupplierProductRouter().router, prefix="/supplier-products")
    admin.include_router(PurchaseOrderRouter().router, prefix="/purchase-orders")
    admin.include_router(POItemRouter().router, prefix="/purchase-order-items")
    admin.include_router(SaleRouter().router, prefix="/sales")
    admin.include_router(AdjustmentRouter().router, prefix="/adjustments")
    admin.include_router(AdjustmentItemRouter().router, prefix="/adjustment-items")
    admin.include_router(TransferRouter().router, prefix="/transfers")
    admin.include_router(TransferItemRouter().router, prefix="/transfer-items")
    admin.include_router(AlertRouter().router, prefix="/alerts")
    admin.include_router(UserAdminRouter().router, prefix="/users")
    admin.include_router(ReportRouter().router, prefix="/reports/inventory")
    app.include_router(admin)
    return app


_APP = _build_admin_app()


def _tree_contains_call(dep: Dependant, target) -> bool:
    if dep.call is target:
        return True
    return any(_tree_contains_call(sub, target) for sub in dep.dependencies)


def _admin_routes() -> list[APIRoute]:
    return [
        r
        for r in _APP.routes
        if isinstance(r, APIRoute) and r.path.startswith("/api/admin")
    ]


def test_every_admin_route_requires_authenticated_user():
    unprotected: list[str] = []
    for route in _admin_routes():
        if not _tree_contains_call(route.dependant, get_current_user):
            for method in sorted(route.methods or []):
                unprotected.append(f"{method} {route.path}")
    assert not unprotected, (
        "Admin routes missing require_permission/get_current_user:\n  - "
        + "\n  - ".join(unprotected)
    )


def test_admin_routes_exist():
    """Sanity check — the filter is actually finding routes."""
    assert len(_admin_routes()) > 0
