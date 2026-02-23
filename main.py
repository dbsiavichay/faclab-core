import copy
import json

import structlog
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from wireup.integration.fastapi import setup as wireup_fastapi_setup

import src
from config import config
from src.catalog.product.infra.routes import CategoryRouter, ProductRouter
from src.catalog.uom.infra.routes import UnitOfMeasureRouter
from src.container import create_wireup_container
from src.customers.infra.routes import CustomerContactRouter, CustomerRouter
from src.inventory.location.infra.routes import LocationRouter
from src.inventory.movement.infra.routes import MovementRouter
from src.inventory.stock.infra.routes import StockRouter
from src.inventory.warehouse.infra.routes import WarehouseRouter
from src.pos.infra.routes import POSCustomerRouter, POSProductRouter
from src.pos.sales.infra.routes import POSSaleRouter
from src.purchasing.infra.routes import POItemRouter, PurchaseOrderRouter
from src.sales.infra.admin_routes import AdminSaleRouter
from src.shared.infra.adapters import OpenTelemetry
from src.shared.infra.logging import configure_logging
from src.shared.infra.middlewares import ErrorHandlingMiddleware
from src.suppliers.infra.routes import (
    SupplierContactRouter,
    SupplierProductRouter,
    SupplierRouter,
)

configure_logging(
    log_level=config.LOG_LEVEL,
    json_output=config.ENVIRONMENT != "local",
)

logger = structlog.get_logger(__name__)

origins = ["http://localhost:3000", "http://localhost:5173"]

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

_docs = config.get_docs_config()

app = FastAPI(
    title=_docs.title,
    version=_docs.version,
    description=_docs.description,
    openapi_tags=_docs.openapi_tags,
    docs_url=None,
    redoc_url=None,
)


def _custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=_docs.openapi_tags,
    )
    schema["x-tagGroups"] = _docs.tag_groups
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi  # type: ignore[method-assign]

# ---------------------------------------------------------------------------
# Scalar docs helpers
# ---------------------------------------------------------------------------

_SCALAR_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏷️</text></svg>" />
  <style>body {{ margin: 0; }}</style>
</head>
<body>
  <script
    id="api-reference"
    data-url="{schema_url}"
    data-configuration='{config}'
  ></script>
  <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>"""


def _scalar_response(title: str, schema_url: str) -> HTMLResponse:
    cfg = json.dumps({"layout": "sidebar", "theme": "default", "searchHotKey": "k"})
    return HTMLResponse(
        _SCALAR_TEMPLATE.format(title=title, schema_url=schema_url, config=cfg)
    )


def _filtered_schema(tag_prefix: str) -> dict:
    """Return a deepcopy of the full schema containing only operations whose tags start with *tag_prefix*."""
    schema = copy.deepcopy(app.openapi())
    used_tags: set[str] = set()
    filtered_paths: dict = {}

    for path, path_item in schema.get("paths", {}).items():
        filtered_ops: dict = {}
        for method, operation in path_item.items():
            if isinstance(operation, dict) and any(
                t.startswith(tag_prefix) for t in operation.get("tags", [])
            ):
                filtered_ops[method] = operation
                used_tags.update(operation.get("tags", []))
        if filtered_ops:
            filtered_paths[path] = filtered_ops

    schema["paths"] = filtered_paths
    schema["tags"] = [t for t in schema.get("tags", []) if t["name"] in used_tags]
    schema["x-tagGroups"] = [
        g
        for g in schema.get("x-tagGroups", [])
        if any(t in used_tags for t in g["tags"])
    ]
    return schema


# ---------------------------------------------------------------------------
# OTEL + DI
# ---------------------------------------------------------------------------

otel = OpenTelemetry()
otel.instrument(app, config.get_otel_config())

wireup_container = create_wireup_container()
src.wireup_container = wireup_container

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Admin API
admin_router = APIRouter(prefix="/api/admin")
admin_router.include_router(
    CategoryRouter().router, prefix="/categories", tags=["admin - categories"]
)
admin_router.include_router(
    UnitOfMeasureRouter().router,
    prefix="/units-of-measure",
    tags=["admin - units of measure"],
)
admin_router.include_router(
    ProductRouter().router, prefix="/products", tags=["admin - products"]
)
admin_router.include_router(
    WarehouseRouter().router, prefix="/warehouses", tags=["admin - warehouses"]
)
admin_router.include_router(
    LocationRouter().router, prefix="/locations", tags=["admin - locations"]
)
admin_router.include_router(
    StockRouter().router, prefix="/stock", tags=["admin - stock"]
)
admin_router.include_router(
    MovementRouter().router, prefix="/movements", tags=["admin - movements"]
)
admin_router.include_router(
    CustomerRouter().router, prefix="/customers", tags=["admin - customers"]
)
admin_router.include_router(
    CustomerContactRouter().router,
    prefix="/customer-contacts",
    tags=["admin - customer-contacts"],
)
admin_router.include_router(
    SupplierRouter().router, prefix="/suppliers", tags=["admin - suppliers"]
)
admin_router.include_router(
    SupplierContactRouter().router,
    prefix="/supplier-contacts",
    tags=["admin - supplier-contacts"],
)
admin_router.include_router(
    SupplierProductRouter().router,
    prefix="/supplier-products",
    tags=["admin - supplier-products"],
)
admin_router.include_router(
    PurchaseOrderRouter().router,
    prefix="/purchase-orders",
    tags=["admin - purchase-orders"],
)
admin_router.include_router(
    POItemRouter().router,
    prefix="/purchase-order-items",
    tags=["admin - purchase-order-items"],
)
admin_router.include_router(
    AdminSaleRouter().router, prefix="/sales", tags=["admin - sales"]
)

# POS API
pos_router = APIRouter(prefix="/api/pos")
pos_router.include_router(POSSaleRouter().router, prefix="/sales", tags=["pos - sales"])
pos_router.include_router(
    POSProductRouter().router, prefix="/products", tags=["pos - products"]
)
pos_router.include_router(
    POSCustomerRouter().router, prefix="/customers", tags=["pos - customers"]
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlingMiddleware)

app.include_router(admin_router)
app.include_router(pos_router)

# ---------------------------------------------------------------------------
# Doc endpoints (only registered when DOCS_ENABLED=true)
# ---------------------------------------------------------------------------

if _docs.enabled:

    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        """Interactive API reference — all endpoints."""
        return _scalar_response(f"{_docs.title} — Reference", "/openapi.json")

    @app.get("/docs/admin", include_in_schema=False)
    async def scalar_admin_docs():
        """Interactive API reference — Admin endpoints only."""
        return _scalar_response(f"{_docs.title} — Admin", "/openapi/admin.json")

    @app.get("/docs/pos", include_in_schema=False)
    async def scalar_pos_docs():
        """Interactive API reference — POS endpoints only."""
        return _scalar_response(f"{_docs.title} — POS", "/openapi/pos.json")

    @app.get("/openapi/admin.json", include_in_schema=False)
    async def admin_openapi_schema():
        return JSONResponse(_filtered_schema("admin"))

    @app.get("/openapi/pos.json", include_in_schema=False)
    async def pos_openapi_schema():
        return JSONResponse(_filtered_schema("pos"))


# ---------------------------------------------------------------------------
# Root + lifecycle
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.on_event("shutdown")
async def shutdown_event():
    otel.shutdown()


wireup_fastapi_setup(wireup_container, app)


if __name__ == "__main__":
    import uvicorn

    logger.info("starting_api")
    uvicorn.run(app, host="0.0.0.0", port=3000)
