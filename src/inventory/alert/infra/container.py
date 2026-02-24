from src.inventory.alert.app.queries.alerts import (
    GetExpiringLotsAlertsQueryHandler,
    GetLowStockAlertsQueryHandler,
    GetOutOfStockAlertsQueryHandler,
    GetReorderPointAlertsQueryHandler,
)

ALERT_INJECTABLES = [
    GetLowStockAlertsQueryHandler,
    GetOutOfStockAlertsQueryHandler,
    GetReorderPointAlertsQueryHandler,
    GetExpiringLotsAlertsQueryHandler,
]
