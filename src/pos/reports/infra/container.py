from src.pos.reports.app.queries.by_payment_method import (
    GetSalesByPaymentMethodQueryHandler,
)
from src.pos.reports.app.queries.daily_summary import GetDailySummaryQueryHandler
from src.pos.reports.app.queries.x_report import GetXReportQueryHandler
from src.pos.reports.app.queries.z_report import GetZReportQueryHandler

POS_REPORT_INJECTABLES = [
    GetXReportQueryHandler,
    GetZReportQueryHandler,
    GetDailySummaryQueryHandler,
    GetSalesByPaymentMethodQueryHandler,
]
