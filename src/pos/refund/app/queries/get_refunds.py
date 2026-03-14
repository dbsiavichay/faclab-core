from dataclasses import dataclass

from wireup import injectable

from src.pos.refund.domain.entities import Refund, RefundItem, RefundPayment
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetRefundByIdQuery(Query):
    refund_id: int


@injectable(lifetime="scoped")
class GetRefundByIdQueryHandler(QueryHandler[GetRefundByIdQuery, dict]):
    def __init__(
        self,
        refund_repo: Repository[Refund],
        refund_item_repo: Repository[RefundItem],
        refund_payment_repo: Repository[RefundPayment],
    ):
        self.refund_repo = refund_repo
        self.refund_item_repo = refund_item_repo
        self.refund_payment_repo = refund_payment_repo

    def _handle(self, query: GetRefundByIdQuery) -> dict:
        refund = self.refund_repo.get_by_id(query.refund_id)
        if not refund:
            raise NotFoundError(f"Refund with id {query.refund_id} not found")

        items = self.refund_item_repo.filter_by(refund_id=query.refund_id)
        payments = self.refund_payment_repo.filter_by(refund_id=query.refund_id)

        result = refund.dict()
        result["items"] = [{**item.dict(), "subtotal": item.subtotal} for item in items]
        result["payments"] = [p.dict() for p in payments]
        return result


@dataclass
class GetRefundsQuery(Query):
    sale_id: int | None = None
    status: str | None = None
    limit: int | None = 100
    offset: int | None = 0


@injectable(lifetime="scoped")
class GetRefundsQueryHandler(QueryHandler[GetRefundsQuery, dict]):
    def __init__(self, refund_repo: Repository[Refund]):
        self.refund_repo = refund_repo

    def _handle(self, query: GetRefundsQuery) -> dict:
        filters = {}
        if query.sale_id is not None:
            filters["original_sale_id"] = query.sale_id
        if query.status is not None:
            filters["status"] = query.status

        return self.refund_repo.paginate(
            limit=query.limit, offset=query.offset, **filters
        )
