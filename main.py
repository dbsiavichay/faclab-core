import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src import initialize
from src.catalog.product.infra.routes import CategoryRouter, ProductRouter
from src.customers.infra.routes import CustomerContactRouter, CustomerRouter
from src.inventory.movement.infra.routes import MovementRouter
from src.inventory.stock.infra.routes import StockRouter
from src.shared.infra.middlewares import ErrorHandlingMiddleware

category_router = CategoryRouter()
product_router = ProductRouter()
stock_router = StockRouter()
movement_router = MovementRouter()
customer_router = CustomerRouter()
customer_contact_router = CustomerContactRouter()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")


origins = ["http://localhost:3000", "http://localhost:5173"]

initialize()

app = FastAPI()


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


@app.get("/")
async def root():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn

    # Iniciar el servidor
    logging.info("Starting Warehouse API with dependency injection container")
    uvicorn.run(app, host="0.0.0.0", port=3000)
