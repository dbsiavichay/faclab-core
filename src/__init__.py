from config import config

# Global wireup container instance (initialized in main.py)
wireup_container = None


def create_wireup_container():
    """Creates and configures wireup container with all injectables.

    Returns:
        Container: Configured wireup dependency injection container
    """
    from wireup import create_sync_container

    from src.catalog.product.app.commands.create_category import (
        CreateCategoryCommandHandler,
    )
    from src.catalog.product.app.commands.create_product import (
        CreateProductCommandHandler,
    )
    from src.catalog.product.app.commands.delete_category import (
        DeleteCategoryCommandHandler,
    )
    from src.catalog.product.app.commands.delete_product import (
        DeleteProductCommandHandler,
    )
    from src.catalog.product.app.commands.update_category import (
        UpdateCategoryCommandHandler,
    )
    from src.catalog.product.app.commands.update_product import (
        UpdateProductCommandHandler,
    )
    from src.catalog.product.app.queries.get_categories import (
        GetAllCategoriesQueryHandler,
        GetCategoryByIdQueryHandler,
    )
    from src.catalog.product.app.queries.get_products import (
        GetAllProductsQueryHandler,
        GetProductByIdQueryHandler,
        SearchProductsQueryHandler,
    )
    from src.catalog.product.infra.controllers import (
        CategoryController,
        ProductController,
    )
    from src.catalog.product.infra.mappers import CategoryMapper, ProductMapper
    from src.catalog.product.infra.repositories import (
        create_category_repository,
        create_product_repository,
    )
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
    from src.inventory.stock.app.queries.stock import (
        GetAllStocksQueryHandler,
        GetStockByIdQueryHandler,
        GetStockByProductQueryHandler,
    )
    from src.inventory.stock.infra.controllers import StockController
    from src.inventory.stock.infra.mappers import StockMapper
    from src.inventory.stock.infra.repositories import create_stock_repository
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
    from src.shared.infra.db_session import configure_session_factory, get_db_session

    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found in environment")

    configure_session_factory(db_connection_string)

    container = create_sync_container(
        injectables=[
            get_db_session,
            CategoryMapper,
            create_category_repository,
            CreateCategoryCommandHandler,
            UpdateCategoryCommandHandler,
            DeleteCategoryCommandHandler,
            GetAllCategoriesQueryHandler,
            GetCategoryByIdQueryHandler,
            CategoryController,
            ProductMapper,
            create_product_repository,
            CreateProductCommandHandler,
            UpdateProductCommandHandler,
            DeleteProductCommandHandler,
            GetAllProductsQueryHandler,
            GetProductByIdQueryHandler,
            SearchProductsQueryHandler,
            ProductController,
            MovementMapper,
            create_movement_repository,
            CreateMovementCommandHandler,
            GetAllMovementsQueryHandler,
            GetMovementByIdQueryHandler,
            MovementController,
            StockMapper,
            create_stock_repository,
            GetAllStocksQueryHandler,
            GetStockByIdQueryHandler,
            GetStockByProductQueryHandler,
            StockController,
            CustomerMapper,
            CustomerContactMapper,
            create_customer_repository,
            create_customer_contact_repository,
            CreateCustomerCommandHandler,
            UpdateCustomerCommandHandler,
            DeleteCustomerCommandHandler,
            ActivateCustomerCommandHandler,
            DeactivateCustomerCommandHandler,
            GetAllCustomersQueryHandler,
            GetCustomerByIdQueryHandler,
            GetCustomerByTaxIdQueryHandler,
            CreateCustomerContactCommandHandler,
            UpdateCustomerContactCommandHandler,
            DeleteCustomerContactCommandHandler,
            GetCustomerContactByIdQueryHandler,
            GetContactsByCustomerIdQueryHandler,
            CustomerController,
            CustomerContactController,
            SaleMapper,
            SaleItemMapper,
            PaymentMapper,
            create_sale_repository,
            create_sale_item_repository,
            create_payment_repository,
            CreateSaleCommandHandler,
            AddSaleItemCommandHandler,
            RemoveSaleItemCommandHandler,
            ConfirmSaleCommandHandler,
            CancelSaleCommandHandler,
            RegisterPaymentCommandHandler,
            GetAllSalesQueryHandler,
            GetSaleByIdQueryHandler,
            GetSaleItemsQueryHandler,
            GetSalePaymentsQueryHandler,
            SaleController,
        ]
    )

    import src.inventory.infra.event_handlers  # noqa: F401
    import src.inventory.stock.infra.event_handlers  # noqa: F401

    return container
