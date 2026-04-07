from dataclasses import dataclass

from wireup import injectable

from src.purchasing.app.repositories import PurchaseReceiptRepository
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetReceiptsByPurchaseOrderQuery(Query):
    purchase_order_id: int = 0


@injectable(lifetime="scoped")
class GetReceiptsByPurchaseOrderQueryHandler(
    QueryHandler[GetReceiptsByPurchaseOrderQuery, list[dict]]
):
    def __init__(self, repo: PurchaseReceiptRepository):
        self.repo = repo

    def _handle(self, query: GetReceiptsByPurchaseOrderQuery) -> list[dict]:
        receipts = self.repo.filter_by(purchase_order_id=query.purchase_order_id)
        return [receipt.dict() for receipt in receipts]
