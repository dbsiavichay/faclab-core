from dataclasses import dataclass

from wireup import injectable

from src.purchasing.app.repositories import PurchaseOrderItemRepository
from src.shared.app.queries import Query, QueryHandler


@dataclass
class GetPurchaseOrderItemsByPOQuery(Query):
    purchase_order_id: int = 0


@injectable(lifetime="scoped")
class GetPurchaseOrderItemsByPOQueryHandler(
    QueryHandler[GetPurchaseOrderItemsByPOQuery, list[dict]]
):
    def __init__(self, repo: PurchaseOrderItemRepository):
        self.repo = repo

    def _handle(self, query: GetPurchaseOrderItemsByPOQuery) -> list[dict]:
        items = self.repo.filter_by(purchase_order_id=query.purchase_order_id)
        return [item.dict() for item in items]
