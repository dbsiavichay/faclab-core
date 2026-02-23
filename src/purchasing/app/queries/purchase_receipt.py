from dataclasses import dataclass

from wireup import injectable

from src.purchasing.domain.entities import PurchaseReceipt
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetReceiptsByPurchaseOrderQuery(Query):
    purchase_order_id: int = 0


@injectable(lifetime="scoped")
class GetReceiptsByPurchaseOrderQueryHandler(
    QueryHandler[GetReceiptsByPurchaseOrderQuery, list[dict]]
):
    def __init__(self, repo: Repository[PurchaseReceipt]):
        self.repo = repo

    def _handle(self, query: GetReceiptsByPurchaseOrderQuery) -> list[dict]:
        receipts = self.repo.filter_by(purchase_order_id=query.purchase_order_id)
        return [receipt.dict() for receipt in receipts]
