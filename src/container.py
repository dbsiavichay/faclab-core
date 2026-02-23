from config import config


def create_wireup_container():
    from wireup import create_async_container

    from src.catalog.product.infra.container import INJECTABLES as CATALOG_INJECTABLES
    from src.catalog.uom.infra.container import INJECTABLES as UOM_INJECTABLES
    from src.customers.infra.container import INJECTABLES as CUSTOMER_INJECTABLES
    from src.inventory.location.infra.container import (
        INJECTABLES as LOCATION_INJECTABLES,
    )
    from src.inventory.movement.infra.container import (
        INJECTABLES as MOVEMENT_INJECTABLES,
    )
    from src.inventory.stock.infra.container import INJECTABLES as STOCK_INJECTABLES
    from src.inventory.warehouse.infra.container import (
        INJECTABLES as WAREHOUSE_INJECTABLES,
    )
    from src.pos.sales.infra.container import INJECTABLES as POS_SALES_INJECTABLES
    from src.sales.infra.container import INJECTABLES as SALES_INJECTABLES
    from src.shared.infra.database import create_session_factory
    from src.shared.infra.events.event_bus_publisher import EventBusPublisher
    from src.suppliers.infra.container import INJECTABLES as SUPPLIER_INJECTABLES

    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found in environment")

    get_db_session = create_session_factory(db_connection_string)

    container = create_async_container(
        injectables=[
            get_db_session,
            EventBusPublisher,
            *CATALOG_INJECTABLES,
            *UOM_INJECTABLES,
            *WAREHOUSE_INJECTABLES,
            *LOCATION_INJECTABLES,
            *MOVEMENT_INJECTABLES,
            *STOCK_INJECTABLES,
            *CUSTOMER_INJECTABLES,
            *SUPPLIER_INJECTABLES,
            *SALES_INJECTABLES,
            *POS_SALES_INJECTABLES,
        ]
    )

    import src.inventory.infra.event_handlers  # noqa: F401
    import src.inventory.stock.infra.event_handlers  # noqa: F401

    return container
