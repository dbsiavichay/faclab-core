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
    # Register the customer mapper
    container.register(
        CustomerMapper,
        factory=lambda c: CustomerMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the customer contact mapper
    container.register(
        CustomerContactMapper,
        factory=lambda c: CustomerContactMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the sale mapper
    container.register(
        SaleMapper,
        factory=lambda c: SaleMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the sale item mapper
    container.register(
        SaleItemMapper,
        factory=lambda c: SaleItemMapper(),
        scope=LifetimeScope.SINGLETON,
    )
    # Register the payment mapper
    container.register(
        PaymentMapper,
        factory=lambda c: PaymentMapper(),
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
    # Register the customer repository
    container.register(
        Repository[Customer],
        factory=lambda c, scope_id=None: CustomerRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(CustomerMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the customer contact repository
    container.register(
        Repository[CustomerContact],
        factory=lambda c, scope_id=None: CustomerContactRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(CustomerContactMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the sale repository
    container.register(
        Repository[Sale],
        factory=lambda c, scope_id=None: SaleRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(SaleMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the sale item repository
    container.register(
        Repository[SaleItem],
        factory=lambda c, scope_id=None: SaleItemRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(SaleItemMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the payment repository
    container.register(
        Repository[Payment],
        factory=lambda c, scope_id=None: PaymentRepositoryImpl(
            c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
            c.resolve(PaymentMapper),
        ),
        scope=LifetimeScope.SCOPED,
    )


def init_use_cases() -> None:
    """Initializes all use cases and command/query handlers."""
    # Register Category command handlers
    container.register(
        CreateCategoryCommandHandler,
        factory=lambda c, scope_id=None: CreateCategoryCommandHandler(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        UpdateCategoryCommandHandler,
        factory=lambda c, scope_id=None: UpdateCategoryCommandHandler(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteCategoryCommandHandler,
        factory=lambda c, scope_id=None: DeleteCategoryCommandHandler(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Category query handlers
    container.register(
        GetAllCategoriesQueryHandler,
        factory=lambda c, scope_id=None: GetAllCategoriesQueryHandler(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetCategoryByIdQueryHandler,
        factory=lambda c, scope_id=None: GetCategoryByIdQueryHandler(
            c.resolve_scoped(Repository[Category], scope_id)
            if scope_id
            else c.resolve(Repository[Category])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Product command handlers
    container.register(
        CreateProductCommandHandler,
        factory=lambda c, scope_id=None: CreateProductCommandHandler(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        UpdateProductCommandHandler,
        factory=lambda c, scope_id=None: UpdateProductCommandHandler(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteProductCommandHandler,
        factory=lambda c, scope_id=None: DeleteProductCommandHandler(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Product query handlers
    container.register(
        GetAllProductsQueryHandler,
        factory=lambda c, scope_id=None: GetAllProductsQueryHandler(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetProductByIdQueryHandler,
        factory=lambda c, scope_id=None: GetProductByIdQueryHandler(
            c.resolve_scoped(Repository[Product], scope_id)
            if scope_id
            else c.resolve(Repository[Product])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Movement command handlers
    container.register(
        CreateMovementCommandHandler,
        factory=lambda c, scope_id=None: CreateMovementCommandHandler(
            c.resolve_scoped(Repository[Movement], scope_id)
            if scope_id
            else c.resolve(Repository[Movement])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Movement query handlers
    container.register(
        GetAllMovementsQueryHandler,
        factory=lambda c, scope_id=None: GetAllMovementsQueryHandler(
            c.resolve_scoped(Repository[Movement], scope_id)
            if scope_id
            else c.resolve(Repository[Movement])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetMovementByIdQueryHandler,
        factory=lambda c, scope_id=None: GetMovementByIdQueryHandler(
            c.resolve_scoped(Repository[Movement], scope_id)
            if scope_id
            else c.resolve(Repository[Movement])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register Stock query handlers
    container.register(
        GetAllStocksQueryHandler,
        factory=lambda c, scope_id=None: GetAllStocksQueryHandler(
            c.resolve_scoped(Repository[Stock], scope_id)
            if scope_id
            else c.resolve(Repository[Stock])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetStockByIdQueryHandler,
        factory=lambda c, scope_id=None: GetStockByIdQueryHandler(
            c.resolve_scoped(Repository[Stock], scope_id)
            if scope_id
            else c.resolve(Repository[Stock])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetStockByProductQueryHandler,
        factory=lambda c, scope_id=None: GetStockByProductQueryHandler(
            c.resolve_scoped(Repository[Stock], scope_id)
            if scope_id
            else c.resolve(Repository[Stock])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register customer command handlers
    container.register(
        CreateCustomerCommandHandler,
        factory=lambda c, scope_id=None: CreateCustomerCommandHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        UpdateCustomerCommandHandler,
        factory=lambda c, scope_id=None: UpdateCustomerCommandHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteCustomerCommandHandler,
        factory=lambda c, scope_id=None: DeleteCustomerCommandHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        ActivateCustomerCommandHandler,
        factory=lambda c, scope_id=None: ActivateCustomerCommandHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeactivateCustomerCommandHandler,
        factory=lambda c, scope_id=None: DeactivateCustomerCommandHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register customer query handlers
    container.register(
        GetAllCustomersQueryHandler,
        factory=lambda c, scope_id=None: GetAllCustomersQueryHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetCustomerByIdQueryHandler,
        factory=lambda c, scope_id=None: GetCustomerByIdQueryHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetCustomerByTaxIdQueryHandler,
        factory=lambda c, scope_id=None: GetCustomerByTaxIdQueryHandler(
            c.resolve_scoped(Repository[Customer], scope_id)
            if scope_id
            else c.resolve(Repository[Customer])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register customer contact command handlers
    container.register(
        CreateCustomerContactCommandHandler,
        factory=lambda c, scope_id=None: CreateCustomerContactCommandHandler(
            c.resolve_scoped(Repository[CustomerContact], scope_id)
            if scope_id
            else c.resolve(Repository[CustomerContact])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        UpdateCustomerContactCommandHandler,
        factory=lambda c, scope_id=None: UpdateCustomerContactCommandHandler(
            c.resolve_scoped(Repository[CustomerContact], scope_id)
            if scope_id
            else c.resolve(Repository[CustomerContact])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        DeleteCustomerContactCommandHandler,
        factory=lambda c, scope_id=None: DeleteCustomerContactCommandHandler(
            c.resolve_scoped(Repository[CustomerContact], scope_id)
            if scope_id
            else c.resolve(Repository[CustomerContact])
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register customer contact query handlers
    container.register(
        GetCustomerContactByIdQueryHandler,
        factory=lambda c, scope_id=None: GetCustomerContactByIdQueryHandler(
            c.resolve_scoped(Repository[CustomerContact], scope_id)
            if scope_id
            else c.resolve(Repository[CustomerContact])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetContactsByCustomerIdQueryHandler,
        factory=lambda c, scope_id=None: GetContactsByCustomerIdQueryHandler(
            c.resolve_scoped(Repository[CustomerContact], scope_id)
            if scope_id
            else c.resolve(Repository[CustomerContact])
        ),
        scope=LifetimeScope.SCOPED,
    )

    # Register sales command handlers
    container.register(
        CreateSaleCommandHandler,
        factory=lambda c, scope_id=None: CreateSaleCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        AddSaleItemCommandHandler,
        factory=lambda c, scope_id=None: AddSaleItemCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale]),
            c.resolve_scoped(Repository[SaleItem], scope_id)
            if scope_id
            else c.resolve(Repository[SaleItem]),
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        RemoveSaleItemCommandHandler,
        factory=lambda c, scope_id=None: RemoveSaleItemCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale]),
            c.resolve_scoped(Repository[SaleItem], scope_id)
            if scope_id
            else c.resolve(Repository[SaleItem]),
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        ConfirmSaleCommandHandler,
        factory=lambda c, scope_id=None: ConfirmSaleCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale]),
            c.resolve_scoped(Repository[SaleItem], scope_id)
            if scope_id
            else c.resolve(Repository[SaleItem]),
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        CancelSaleCommandHandler,
        factory=lambda c, scope_id=None: CancelSaleCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale]),
            c.resolve_scoped(Repository[SaleItem], scope_id)
            if scope_id
            else c.resolve(Repository[SaleItem]),
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        RegisterPaymentCommandHandler,
        factory=lambda c, scope_id=None: RegisterPaymentCommandHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale]),
            c.resolve_scoped(Repository[Payment], scope_id)
            if scope_id
            else c.resolve(Repository[Payment]),
        ),
        scope=LifetimeScope.SCOPED,
    )

    # Register sales query handlers
    container.register(
        GetAllSalesQueryHandler,
        factory=lambda c, scope_id=None: GetAllSalesQueryHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetSaleByIdQueryHandler,
        factory=lambda c, scope_id=None: GetSaleByIdQueryHandler(
            c.resolve_scoped(Repository[Sale], scope_id)
            if scope_id
            else c.resolve(Repository[Sale])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetSaleItemsQueryHandler,
        factory=lambda c, scope_id=None: GetSaleItemsQueryHandler(
            c.resolve_scoped(Repository[SaleItem], scope_id)
            if scope_id
            else c.resolve(Repository[SaleItem])
        ),
        scope=LifetimeScope.SCOPED,
    )
    container.register(
        GetSalePaymentsQueryHandler,
        factory=lambda c, scope_id=None: GetSalePaymentsQueryHandler(
            c.resolve_scoped(Repository[Payment], scope_id)
            if scope_id
            else c.resolve(Repository[Payment])
        ),
        scope=LifetimeScope.SCOPED,
    )


def init_controllers() -> None:
    """Initializes all controllers."""
    # Register the category controller
    container.register(
        CategoryController,
        factory=lambda c, scope_id=None: CategoryController(
            c.resolve_scoped(CreateCategoryCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateCategoryCommandHandler),
            c.resolve_scoped(UpdateCategoryCommandHandler, scope_id)
            if scope_id
            else c.resolve(UpdateCategoryCommandHandler),
            c.resolve_scoped(DeleteCategoryCommandHandler, scope_id)
            if scope_id
            else c.resolve(DeleteCategoryCommandHandler),
            c.resolve_scoped(GetAllCategoriesQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllCategoriesQueryHandler),
            c.resolve_scoped(GetCategoryByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetCategoryByIdQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the product controller
    container.register(
        ProductController,
        factory=lambda c, scope_id=None: ProductController(
            c.resolve_scoped(CreateProductCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateProductCommandHandler),
            c.resolve_scoped(UpdateProductCommandHandler, scope_id)
            if scope_id
            else c.resolve(UpdateProductCommandHandler),
            c.resolve_scoped(DeleteProductCommandHandler, scope_id)
            if scope_id
            else c.resolve(DeleteProductCommandHandler),
            c.resolve_scoped(GetAllProductsQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllProductsQueryHandler),
            c.resolve_scoped(GetProductByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetProductByIdQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the stock controller
    container.register(
        StockController,
        factory=lambda c, scope_id=None: StockController(
            c.resolve_scoped(GetAllStocksQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllStocksQueryHandler),
            c.resolve_scoped(GetStockByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetStockByIdQueryHandler),
            c.resolve_scoped(GetStockByProductQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetStockByProductQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the movement controller
    container.register(
        MovementController,
        factory=lambda c, scope_id=None: MovementController(
            c.resolve_scoped(CreateMovementCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateMovementCommandHandler),
            c.resolve_scoped(GetAllMovementsQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllMovementsQueryHandler),
            c.resolve_scoped(GetMovementByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetMovementByIdQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the customer controller
    container.register(
        CustomerController,
        factory=lambda c, scope_id=None: CustomerController(
            c.resolve_scoped(CreateCustomerCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateCustomerCommandHandler),
            c.resolve_scoped(UpdateCustomerCommandHandler, scope_id)
            if scope_id
            else c.resolve(UpdateCustomerCommandHandler),
            c.resolve_scoped(DeleteCustomerCommandHandler, scope_id)
            if scope_id
            else c.resolve(DeleteCustomerCommandHandler),
            c.resolve_scoped(ActivateCustomerCommandHandler, scope_id)
            if scope_id
            else c.resolve(ActivateCustomerCommandHandler),
            c.resolve_scoped(DeactivateCustomerCommandHandler, scope_id)
            if scope_id
            else c.resolve(DeactivateCustomerCommandHandler),
            c.resolve_scoped(GetAllCustomersQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllCustomersQueryHandler),
            c.resolve_scoped(GetCustomerByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetCustomerByIdQueryHandler),
            c.resolve_scoped(GetCustomerByTaxIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetCustomerByTaxIdQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the customer contact controller
    container.register(
        CustomerContactController,
        factory=lambda c, scope_id=None: CustomerContactController(
            c.resolve_scoped(CreateCustomerContactCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateCustomerContactCommandHandler),
            c.resolve_scoped(UpdateCustomerContactCommandHandler, scope_id)
            if scope_id
            else c.resolve(UpdateCustomerContactCommandHandler),
            c.resolve_scoped(DeleteCustomerContactCommandHandler, scope_id)
            if scope_id
            else c.resolve(DeleteCustomerContactCommandHandler),
            c.resolve_scoped(GetCustomerContactByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetCustomerContactByIdQueryHandler),
            c.resolve_scoped(GetContactsByCustomerIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetContactsByCustomerIdQueryHandler),
        ),
        scope=LifetimeScope.SCOPED,
    )
    # Register the sale controller
    container.register(
        SaleController,
        factory=lambda c, scope_id=None: SaleController(
            c.resolve_scoped(CreateSaleCommandHandler, scope_id)
            if scope_id
            else c.resolve(CreateSaleCommandHandler),
            c.resolve_scoped(AddSaleItemCommandHandler, scope_id)
            if scope_id
            else c.resolve(AddSaleItemCommandHandler),
            c.resolve_scoped(RemoveSaleItemCommandHandler, scope_id)
            if scope_id
            else c.resolve(RemoveSaleItemCommandHandler),
            c.resolve_scoped(ConfirmSaleCommandHandler, scope_id)
            if scope_id
            else c.resolve(ConfirmSaleCommandHandler),
            c.resolve_scoped(CancelSaleCommandHandler, scope_id)
            if scope_id
            else c.resolve(CancelSaleCommandHandler),
            c.resolve_scoped(RegisterPaymentCommandHandler, scope_id)
            if scope_id
            else c.resolve(RegisterPaymentCommandHandler),
            c.resolve_scoped(GetAllSalesQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetAllSalesQueryHandler),
            c.resolve_scoped(GetSaleByIdQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetSaleByIdQueryHandler),
            c.resolve_scoped(GetSaleItemsQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetSaleItemsQueryHandler),
            c.resolve_scoped(GetSalePaymentsQueryHandler, scope_id)
            if scope_id
            else c.resolve(GetSalePaymentsQueryHandler),
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

    # Import event handlers to register them via decorators
    import src.inventory.infra.event_handlers  # noqa: F401
    import src.inventory.stock.infra.event_handlers  # noqa: F401


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


# Dependency to get the customer controller in a request scope
def get_customer_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> CustomerController:
    """Gets the customer controller for a specific request."""
    controller = container.resolve_scoped(CustomerController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)


# Dependency to get the customer contact controller in a request scope
def get_customer_contact_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> CustomerContactController:
    """Gets the customer contact controller for a specific request."""
    controller = container.resolve_scoped(CustomerContactController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)


# Dependency to get the sale controller in a request scope
def get_sale_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> SaleController:
    """Gets the sale controller for a specific request."""
    controller = container.resolve_scoped(SaleController, scope_id)
    try:
        yield controller
    finally:
        # Close the scope when the request ends
        container.close_scope(scope_id)
