import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from wireup.integration.fastapi import setup as wireup_fastapi_setup

import src
from config import config
from src import create_wireup_container
from src.catalog.product.infra.routes import CategoryRouter, ProductRouter
from src.customers.infra.routes import CustomerContactRouter, CustomerRouter
from src.inventory.movement.infra.routes import MovementRouter
from src.inventory.stock.infra.routes import StockRouter
from src.sales.infra.routes import SaleRouter
from src.shared.infra.logging import configure_logging
from src.shared.infra.middlewares import ErrorHandlingMiddleware

configure_logging(
    log_level=config.LOG_LEVEL,
    json_output=config.ENVIRONMENT != "local",
)

logger = structlog.get_logger(__name__)

origins = ["http://localhost:3000", "http://localhost:5173"]

wireup_container = create_wireup_container()
src.wireup_container = wireup_container

app = FastAPI(
    title="Faclab core API", version="1.0.0", description="API for Faclab core services"
)


category_router = CategoryRouter()
product_router = ProductRouter()
stock_router = StockRouter()
movement_router = MovementRouter()
customer_router = CustomerRouter()
customer_contact_router = CustomerContactRouter()
sale_router = SaleRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlingMiddleware)

app.include_router(category_router.router, prefix="/categories", tags=["categories"])
app.include_router(product_router.router, prefix="/products", tags=["products"])
app.include_router(stock_router.router, prefix="/stock", tags=["stock"])
app.include_router(movement_router.router, prefix="/movements", tags=["movements"])
app.include_router(customer_router.router, prefix="/customers", tags=["customers"])
app.include_router(
    customer_contact_router.router,
    prefix="/customer-contacts",
    tags=["customer-contacts"],
)
app.include_router(sale_router.router, prefix="/sales", tags=["sales"])


@app.get("/")
async def root():
    return RedirectResponse("/docs")


wireup_fastapi_setup(wireup_container, app)


if __name__ == "__main__":
    import uvicorn

    logger.info("starting_api")
    uvicorn.run(app, host="0.0.0.0", port=3000)
