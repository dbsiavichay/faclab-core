import structlog
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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
from src.sales.infra.admin_routes import AdminSaleRouter
from src.shared.infra.adapters import OpenTelemetry
from src.shared.infra.logging import configure_logging
from src.shared.infra.middlewares import ErrorHandlingMiddleware

configure_logging(
    log_level=config.LOG_LEVEL,
    json_output=config.ENVIRONMENT != "local",
)

logger = structlog.get_logger(__name__)

origins = ["http://localhost:3000", "http://localhost:5173"]

app = FastAPI(
    title="Faclab core API", version="1.0.0", description="API for Faclab core services"
)

otel = OpenTelemetry()
otel.instrument(app, config.get_otel_config())

wireup_container = create_wireup_container()
src.wireup_container = wireup_container

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


@app.get("/")
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
