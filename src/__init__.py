import uuid

from fastapi import Depends

from config import config
from src.catalog.product.app.commands import (
    CreateCategoryCommandHandler,
    CreateProductCommandHandler,
    DeleteCategoryCommandHandler,
    DeleteProductCommandHandler,
    UpdateCategoryCommandHandler,
    UpdateProductCommandHandler,
)
from src.catalog.product.app.queries import (
    GetAllCategoriesQueryHandler,
    GetAllProductsQueryHandler,
    GetCategoryByIdQueryHandler,
    GetProductByIdQueryHandler,
)
from src.catalog.product.domain.entities import Category, Product
from src.catalog.product.infra.controllers import CategoryController, ProductController
from src.catalog.product.infra.mappers import CategoryMapper, ProductMapper
from src.catalog.product.infra.repositories import (
    CategoryRepositoryImpl,
    ProductRepositoryImpl,
)
from src.customers.app.commands import (
    ActivateCustomerCommandHandler,
    CreateCustomerCommandHandler,
    CreateCustomerContactCommandHandler,
    DeactivateCustomerCommandHandler,
    DeleteCustomerCommandHandler,
    DeleteCustomerContactCommandHandler,
    UpdateCustomerCommandHandler,
    UpdateCustomerContactCommandHandler,
)
from src.customers.app.queries import (
    GetAllCustomersQueryHandler,
    GetContactsByCustomerIdQueryHandler,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQueryHandler,
    GetCustomerContactByIdQueryHandler,
)
from src.customers.domain.entities import Customer, CustomerContact
from src.customers.infra.controllers import (
    CustomerContactController,
    CustomerController,
)
from src.customers.infra.mappers import CustomerContactMapper, CustomerMapper
from src.customers.infra.repositories import (
    CustomerContactRepositoryImpl,
    CustomerRepositoryImpl,
)
from src.inventory.movement.app.commands import CreateMovementCommandHandler
from src.inventory.movement.app.queries import (
    GetAllMovementsQueryHandler,
    GetMovementByIdQueryHandler,
)
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.infra.controllers import MovementController
from src.inventory.movement.infra.mappers import MovementMapper
from src.inventory.movement.infra.repositories import MovementRepositoryImpl
from src.inventory.stock.app.queries import (
    GetAllStocksQueryHandler,
    GetStockByIdQueryHandler,
    GetStockByProductQueryHandler,
)
from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.controllers import StockController
from src.inventory.stock.infra.mappers import StockMapper
from src.inventory.stock.infra.repositories import StockRepositoryImpl
from src.sales.app.commands import (
    AddSaleItemCommandHandler,
    CancelSaleCommandHandler,
    ConfirmSaleCommandHandler,
    CreateSaleCommandHandler,
    RegisterPaymentCommandHandler,
    RemoveSaleItemCommandHandler,
)
from src.sales.app.queries import (
    GetAllSalesQueryHandler,
    GetSaleByIdQueryHandler,
    GetSaleItemsQueryHandler,
    GetSalePaymentsQueryHandler,
)
from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.controllers import SaleController
from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
from src.sales.infra.repositories import (
    PaymentRepositoryImpl,
    SaleItemRepositoryImpl,
    SaleRepositoryImpl,
)
from src.shared.infra.di import DependencyContainer, LifetimeScope
from src.shared.infra.repositories import Repository

container = DependencyContainer()


def init_mappers() -> None:
    """Initializes all mappers (legacy custom DI)."""
    # Movement mapper removed - now registered in wireup (Phase 2)
    # Category mapper removed - now registered in wireup (Phase 1)
    # Product mapper removed - now registered in wireup (Phase 2)
    # Stock mapper removed - now registered in wireup (Phase 2)
    # Customer mapper removed - now registered in wireup (Phase 2)
    # CustomerContact mapper removed - now registered in wireup (Phase 2)
    # Sale mappers removed - now registered in wireup (Phase 2)
    pass


def init_repositories() -> None:
    """Initializes all repositories (legacy custom DI)."""
    # Category repository removed - now registered in wireup (Phase 1)
    # Product repository removed - now registered in wireup (Phase 2)
    # Stock repository removed - now registered in wireup (Phase 2)
    # Movement repository removed - now registered in wireup (Phase 2)
    # Customer repository removed - now registered in wireup (Phase 2)
    # CustomerContact repository removed - now registered in wireup (Phase 2)
    # Sale repositories removed - now registered in wireup (Phase 2)
    pass


def init_handlers() -> None:
    """Initializes all command and query handlers for CQRS architecture (legacy custom DI)."""
    # Category handlers removed - now registered in wireup (Phase 1)
    # Product handlers removed - now registered in wireup (Phase 2)
    # Movement handlers removed - now registered in wireup (Phase 2)
    # Stock handlers removed - now registered in wireup (Phase 2)
    # Customer handlers removed - now registered in wireup (Phase 2)
    # CustomerContact handlers removed - now registered in wireup (Phase 2)
    # Sale handlers removed - now registered in wireup (Phase 2)
    pass


def init_controllers() -> None:
    """Initializes all controllers (legacy custom DI)."""
    # CategoryController removed - now registered in wireup (Phase 1)
    # ProductController removed - now registered in wireup (Phase 2)
    # StockController removed - now registered in wireup (Phase 2)
    # MovementController removed - now registered in wireup (Phase 2)
    # CustomerController removed - now registered in wireup (Phase 2)
    # CustomerContactController removed - now registered in wireup (Phase 2)
    # SaleController removed - now registered in wireup (Phase 2)
    pass


def create_wireup_container():
    """Creates and configures wireup container with all injectables.

    This function will be populated during Phase 1+ migration with decorated
    classes from each module. For Phase 0, it establishes the infrastructure.

    Returns:
        Container: Configured wireup dependency injection container
    """
    from wireup import create_sync_container

    from src.shared.infra.db_session import configure_session_factory, get_db_session

    # Phase 1: Import category module components
    from src.catalog.product.app.commands.create_category import (
        CreateCategoryCommandHandler,
    )
    from src.catalog.product.app.commands.delete_category import (
        DeleteCategoryCommandHandler,
    )
    from src.catalog.product.app.commands.update_category import (
        UpdateCategoryCommandHandler,
    )
    from src.catalog.product.app.queries.get_categories import (
        GetAllCategoriesQueryHandler,
        GetCategoryByIdQueryHandler,
    )
    from src.catalog.product.infra.controllers import CategoryController
    from src.catalog.product.infra.mappers import CategoryMapper
    from src.catalog.product.infra.repositories import create_category_repository

    # Phase 2: Import product module components
    from src.catalog.product.app.commands.create_product import (
        CreateProductCommandHandler,
    )
    from src.catalog.product.app.commands.delete_product import (
        DeleteProductCommandHandler,
    )
    from src.catalog.product.app.commands.update_product import (
        UpdateProductCommandHandler,
    )
    from src.catalog.product.app.queries.get_products import (
        GetAllProductsQueryHandler,
        GetProductByIdQueryHandler,
        SearchProductsQueryHandler,
    )
    from src.catalog.product.infra.controllers import ProductController
    from src.catalog.product.infra.mappers import ProductMapper
    from src.catalog.product.infra.repositories import create_product_repository

    # Phase 2: Import movement module components
    from src.inventory.movement.app.commands.movement import (
        CreateMovementCommandHandler,
    )
    from src.inventory.movement.app.queries.movement import (
        GetAllMovementsQueryHandler,
        GetMovementByIdQueryHandler,
    )
    from src.inventory.movement.infra.controllers import MovementController
    from src.inventory.movement.infra.mappers import MovementMapper
    from src.inventory.movement.infra.repositories import create_movement_repository

    # Phase 2: Import stock module components
    from src.inventory.stock.app.queries.stock import (
        GetAllStocksQueryHandler,
        GetStockByIdQueryHandler,
        GetStockByProductQueryHandler,
    )
    from src.inventory.stock.infra.controllers import StockController
    from src.inventory.stock.infra.mappers import StockMapper
    from src.inventory.stock.infra.repositories import create_stock_repository

    # Phase 2: Import customer module components
    from src.customers.app.commands.customer import (
        ActivateCustomerCommandHandler,
        CreateCustomerCommandHandler,
        DeactivateCustomerCommandHandler,
        DeleteCustomerCommandHandler,
        UpdateCustomerCommandHandler,
    )
    from src.customers.app.commands.customer_contact import (
        CreateCustomerContactCommandHandler,
        DeleteCustomerContactCommandHandler,
        UpdateCustomerContactCommandHandler,
    )
    from src.customers.app.queries.customer import (
        GetAllCustomersQueryHandler,
        GetCustomerByIdQueryHandler,
        GetCustomerByTaxIdQueryHandler,
    )
    from src.customers.app.queries.customer_contact import (
        GetContactsByCustomerIdQueryHandler,
        GetCustomerContactByIdQueryHandler,
    )
    from src.customers.infra.controllers import (
        CustomerContactController,
        CustomerController,
    )
    from src.customers.infra.mappers import CustomerContactMapper, CustomerMapper
    from src.customers.infra.repositories import (
        create_customer_contact_repository,
        create_customer_repository,
    )

    # Phase 2: Import sale module components
    from src.sales.app.commands.add_sale_item import AddSaleItemCommandHandler
    from src.sales.app.commands.cancel_sale import CancelSaleCommandHandler
    from src.sales.app.commands.confirm_sale import ConfirmSaleCommandHandler
    from src.sales.app.commands.create_sale import CreateSaleCommandHandler
    from src.sales.app.commands.register_payment import RegisterPaymentCommandHandler
    from src.sales.app.commands.remove_sale_item import RemoveSaleItemCommandHandler
    from src.sales.app.queries.get_payments import GetSalePaymentsQueryHandler
    from src.sales.app.queries.get_sale_items import GetSaleItemsQueryHandler
    from src.sales.app.queries.get_sales import (
        GetAllSalesQueryHandler,
        GetSaleByIdQueryHandler,
    )
    from src.sales.infra.controllers import SaleController
    from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
    from src.sales.infra.repositories import (
        create_payment_repository,
        create_sale_item_repository,
        create_sale_repository,
    )

    # Configure DB connection for wireup session factory
    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found in environment")

    configure_session_factory(db_connection_string)

    # Create container with injectables
    # Phase 0: Only DB session factory registered
    # Phase 1: Category module components added (router uses Injected[] pattern)
    # Phase 2+: Will add remaining modules
    container = create_sync_container(
        injectables=[
            # Shared infrastructure
            get_db_session,  # Scoped session factory with generator cleanup
            # Category module (Phase 1)
            CategoryMapper,  # Singleton mapper
            create_category_repository,  # Scoped repository factory
            CreateCategoryCommandHandler,  # Scoped command handler
            UpdateCategoryCommandHandler,  # Scoped command handler
            DeleteCategoryCommandHandler,  # Scoped command handler
            GetAllCategoriesQueryHandler,  # Scoped query handler
            GetCategoryByIdQueryHandler,  # Scoped query handler
            CategoryController,  # Scoped controller
            # Product module (Phase 2)
            ProductMapper,  # Singleton mapper
            create_product_repository,  # Scoped repository factory
            CreateProductCommandHandler,  # Scoped command handler
            UpdateProductCommandHandler,  # Scoped command handler
            DeleteProductCommandHandler,  # Scoped command handler
            GetAllProductsQueryHandler,  # Scoped query handler
            GetProductByIdQueryHandler,  # Scoped query handler
            SearchProductsQueryHandler,  # Scoped query handler
            ProductController,  # Scoped controller
            # Movement module (Phase 2)
            MovementMapper,  # Singleton mapper
            create_movement_repository,  # Scoped repository factory
            CreateMovementCommandHandler,  # Scoped command handler
            GetAllMovementsQueryHandler,  # Scoped query handler
            GetMovementByIdQueryHandler,  # Scoped query handler
            MovementController,  # Scoped controller
            # Stock module (Phase 2)
            StockMapper,  # Singleton mapper
            create_stock_repository,  # Scoped repository factory
            GetAllStocksQueryHandler,  # Scoped query handler
            GetStockByIdQueryHandler,  # Scoped query handler
            GetStockByProductQueryHandler,  # Scoped query handler
            StockController,  # Scoped controller
            # Customer module (Phase 2)
            CustomerMapper,  # Singleton mapper
            CustomerContactMapper,  # Singleton mapper
            create_customer_repository,  # Scoped repository factory
            create_customer_contact_repository,  # Scoped repository factory
            CreateCustomerCommandHandler,  # Scoped command handler
            UpdateCustomerCommandHandler,  # Scoped command handler
            DeleteCustomerCommandHandler,  # Scoped command handler
            ActivateCustomerCommandHandler,  # Scoped command handler
            DeactivateCustomerCommandHandler,  # Scoped command handler
            GetAllCustomersQueryHandler,  # Scoped query handler
            GetCustomerByIdQueryHandler,  # Scoped query handler
            GetCustomerByTaxIdQueryHandler,  # Scoped query handler
            CreateCustomerContactCommandHandler,  # Scoped command handler
            UpdateCustomerContactCommandHandler,  # Scoped command handler
            DeleteCustomerContactCommandHandler,  # Scoped command handler
            GetCustomerContactByIdQueryHandler,  # Scoped query handler
            GetContactsByCustomerIdQueryHandler,  # Scoped query handler
            CustomerController,  # Scoped controller
            CustomerContactController,  # Scoped controller
            # Sale module (Phase 2)
            SaleMapper,  # Singleton mapper
            SaleItemMapper,  # Singleton mapper
            PaymentMapper,  # Singleton mapper
            create_sale_repository,  # Scoped repository factory
            create_sale_item_repository,  # Scoped repository factory
            create_payment_repository,  # Scoped repository factory
            CreateSaleCommandHandler,  # Scoped command handler
            AddSaleItemCommandHandler,  # Scoped command handler
            RemoveSaleItemCommandHandler,  # Scoped command handler
            ConfirmSaleCommandHandler,  # Scoped command handler
            CancelSaleCommandHandler,  # Scoped command handler
            RegisterPaymentCommandHandler,  # Scoped command handler
            GetAllSalesQueryHandler,  # Scoped query handler
            GetSaleByIdQueryHandler,  # Scoped query handler
            GetSaleItemsQueryHandler,  # Scoped query handler
            GetSalePaymentsQueryHandler,  # Scoped query handler
            SaleController,  # Scoped controller
        ]
    )

    return container


def initialize() -> None:
    """Initializes all application dependencies (custom DI - legacy).

    Note: This function will be removed in Phase 3 after full wireup migration.
    """

    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found in environment")
    container.configure_db(db_connection_string)

    init_mappers()
    init_repositories()
    init_handlers()
    init_controllers()

    # Import event handlers to register them via decorators
    import src.inventory.infra.event_handlers  # noqa: F401
    import src.inventory.stock.infra.event_handlers  # noqa: F401


# Function to generate a unique scope ID for each request
def get_request_scope_id():
    return str(uuid.uuid4())


# get_category_controller removed - CategoryRouter now uses wireup (Phase 1)
# get_product_controller removed - ProductRouter now uses wireup (Phase 2)
# get_movement_controller removed - MovementRouter now uses wireup (Phase 2)
# get_stock_controller removed - StockRouter now uses wireup (Phase 2)
# get_customer_controller removed - CustomerRouter now uses wireup (Phase 2)
# get_customer_contact_controller removed - CustomerContactRouter now uses wireup (Phase 2)
# get_sale_controller removed - SaleRouter now uses wireup (Phase 2)
