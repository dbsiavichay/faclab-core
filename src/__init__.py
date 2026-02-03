import uuid

from fastapi import Depends

from config import config
from src.catalog.product.app.use_cases import (
    CreateCategoryUseCase,
    CreateProductUseCase,
    DeleteCategoryUseCase,
    DeleteProductUseCase,
    GetAllCategoriesUseCase,
    GetAllProductsUseCase,
    GetCategoryByIdUseCase,
    GetProductByIdUseCase,
    UpdateCategoryUseCase,
    UpdateProductUseCase,
)
from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.controllers import CategoryController, ProductController
from src.catalog.product.infra.mappers import CategoryMapper, ProductMapper
from src.catalog.product.infra.repositories import (
    CategoryRepositoryImpl,
    ProductRepositoryImpl,
)
from src.inventory.movement.app.use_cases import (
    CreateMovementUseCase,
    FilterMovementsUseCase,
)
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.controllers import MovementController
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.repositories import MovementRepositoryImpl
from src.inventory.stock.app.use_cases import FilterStocksUseCase
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.controllers import StockController
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.repositories import StockRepositoryImpl
from src.shared.infra.di import DependencyContainer, LifetimeScope
from src.shared.infra.repositories import Repository

container = DependencyContainer()


def init_mappers() -> None:
    """Initializes all mappers."""
    # Register the movement mapper
    container.register(
        MovementMapper,
        factory=lambda c: MovementMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the category mapper
    container.register(
        CategoryMapper,
        factory=lambda c: CategoryMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the product mapper
    container.register(
        ProductMapper,
        factory=lambda c: ProductMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the stock mapper
    container.register(
        StockMapper,
        factory=lambda c: StockMapper(),
        scope=LifetimeScope.SINGLETON,
    )


def init_repositories() -> None:
    """Initializes all repositories."""
    # Register the category repository
    container.register(
        Repository[Category],
        factory=lambda c, scope_id=None: CategoryRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(CategoryMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the product repository
    container.register(
        Repository[Product],
        factory=lambda c, scope_id=None: ProductRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(ProductMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the stock repository
    container.register(
        Repository[Stock],
        factory=lambda c, scope_id=None: StockRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(StockMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the movement repository
    container.register(
        Repository[Movement],
        factory=lambda c, scope_id=None: MovementRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(MovementMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )


def init_use_cases() -> None:
    """Initializes all use cases."""
    # Register the category use cases
    container.register(
        CreateCategoryUseCase,
        factory=lambda c, scope_id=None: CreateCategoryUseCase(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
    )
    container.register(
        UpdateCategoryUseCase,
        factory=lambda c, scope_id=None: UpdateCategoryUseCase(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteCategoryUseCase,
        factory=lambda c, scope_id=None: DeleteCategoryUseCase(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetAllCategoriesUseCase,
        factory=lambda c, scope_id=None: GetAllCategoriesUseCase(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetCategoryByIdUseCase,
        factory=lambda c, scope_id=None: GetCategoryByIdUseCase(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the product use cases
    container.register(
        CreateProductUseCase,
        factory=lambda c, scope_id=None: CreateProductUseCase(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
    )
    container.register(
        UpdateProductUseCase,
        factory=lambda c, scope_id=None: UpdateProductUseCase(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteProductUseCase,
        factory=lambda c, scope_id=None: DeleteProductUseCase(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetAllProductsUseCase,
        factory=lambda c, scope_id=None: GetAllProductsUseCase(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetProductByIdUseCase,
        factory=lambda c, scope_id=None: GetProductByIdUseCase(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register movement use cases
    container.register(
        CreateMovementUseCase,
        factory=lambda c, scope_id=None: CreateMovementUseCase(
            c.resolve_scoped(Repository[Movement], scope_id)
            if scope_id
            else c.resolve(Repository[Movement]),
            c.resolve_scoped(Repository[Stock], scope_id)
            if scope_id
            else c.resolve(Repository[Stock]),
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        FilterMovementsUseCase,
        factory=lambda c, scope_id=None: FilterMovementsUseCase(
            c.resolve_scoped(Repository[Movement], scope_id)
            if scope_id
            else c.resolve(Repository[Movement])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the stock use cases
    container.register(
        FilterStocksUseCase,
        factory=lambda c, scope_id=None: FilterStocksUseCase(
            c.resolve_scoped(Repository[Stock], scope_id)
            if scope_id
            else c.resolve(Repository[Stock])
        ),
        scope=LifetimeScope.SCOPED,
    )


def init_controllers() -> None:
    """Initializes all controllers."""
    # Register the category controller
    container.register(
        CategoryController,
        factory=lambda c, scope_id=None: CategoryController(
            c.resolve_scoped(CreateCategoryUseCase, scope_id)
            if scope_id
            else c.resolve(CreateCategoryUseCase),
            c.resolve_scoped(UpdateCategoryUseCase, scope_id)
            if scope_id
            else c.resolve(UpdateCategoryUseCase),
            c.resolve_scoped(DeleteCategoryUseCase, scope_id)
            if scope_id
            else c.resolve(DeleteCategoryUseCase),
            c.resolve_scoped(GetAllCategoriesUseCase, scope_id)
            if scope_id
            else c.resolve(GetAllCategoriesUseCase),
            c.resolve_scoped(GetCategoryByIdUseCase, scope_id)
            if scope_id
            else c.resolve(GetCategoryByIdUseCase),
        ),
    )
    # Register the product controller
    container.register(
        ProductController,
        factory=lambda c, scope_id=None: ProductController(
            c.resolve_scoped(CreateProductUseCase, scope_id)
            if scope_id
            else c.resolve(CreateProductUseCase),
            c.resolve_scoped(UpdateProductUseCase, scope_id)
            if scope_id
            else c.resolve(UpdateProductUseCase),
            c.resolve_scoped(DeleteProductUseCase, scope_id)
            if scope_id
            else c.resolve(DeleteProductUseCase),
            c.resolve_scoped(GetAllProductsUseCase, scope_id)
            if scope_id
            else c.resolve(GetAllProductsUseCase),
            c.resolve_scoped(GetProductByIdUseCase, scope_id)
            if scope_id
            else c.resolve(GetProductByIdUseCase),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the stock controller
    container.register(
        StockController,
        factory=lambda c, scope_id=None: StockController(
            c.resolve_scoped(FilterStocksUseCase, scope_id)
            if scope_id
            else c.resolve(FilterStocksUseCase)
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the movement controller
    container.register(
        MovementController,
        factory=lambda c, scope_id=None: MovementController(
            c.resolve_scoped(CreateMovementUseCase, scope_id)
            if scope_id
            else c.resolve(CreateMovementUseCase),
            c.resolve_scoped(FilterMovementsUseCase, scope_id)
            if scope_id
            else c.resolve(FilterMovementsUseCase),
        ),
        scope=LifetimeScope.SCOPED,
    )


def initialize() -> None:
    """Initializes all application dependencies."""

    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found in environment")
    container.configure_db(db_connection_string)

    init_mappers()
    init_repositories()
    init_use_cases()
    init_controllers()


# Function to generate a unique scope ID for each request
def get_request_scope_id():
    return str(uuid.uuid4())


# Dependency to get the category controller in a request scope
def get_category_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> CategoryController:
    """Gets the category controller for a specific request."""
    controller = container.resolve_scoped(CategoryController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)


# Dependency to get the product controller in a request scope
def get_product_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> ProductController:
    """Gets the product controller for a specific request."""
    controller = container.resolve_scoped(ProductController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)


# Dependency to get the stock controller in a request scope
def get_stock_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> StockController:
    """Gets the stock controller for a specific request."""
    controller = container.resolve_scoped(StockController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)


# Dependency to get the movement controller in a request scope
def get_movement_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> MovementController:
    """Gets the movement controller for a specific request."""
    controller = container.resolve_scoped(MovementController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)
