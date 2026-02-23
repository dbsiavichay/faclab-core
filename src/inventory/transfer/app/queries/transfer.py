from dataclasses import dataclass

from wireup import injectable

from src.inventory.transfer.domain.entities import StockTransfer, StockTransferItem
from src.inventory.transfer.domain.specifications import (
    TransfersBySourceLocation,
    TransfersByStatus,
)
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class GetAllTransfersQuery(Query):
    status: str | None = None
    source_location_id: int | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllTransfersQueryHandler(QueryHandler[GetAllTransfersQuery, list[dict]]):
    def __init__(self, repo: Repository[StockTransfer]):
        self.repo = repo

    def _handle(self, query: GetAllTransfersQuery) -> list[dict]:
        from src.inventory.transfer.domain.entities import TransferStatus

        spec = None

        if query.status is not None:
            status_spec = TransfersByStatus(TransferStatus(query.status))
            spec = status_spec if spec is None else spec & status_spec

        if query.source_location_id is not None:
            location_spec = TransfersBySourceLocation(query.source_location_id)
            spec = location_spec if spec is None else spec & location_spec

        if spec is not None:
            transfers = self.repo.filter_by_spec(
                spec, limit=query.limit, offset=query.offset
            )
        else:
            transfers = self.repo.filter_by(limit=query.limit, offset=query.offset)

        return [t.dict() for t in transfers]


@dataclass
class GetTransferByIdQuery(Query):
    id: int = 0


@injectable(lifetime="scoped")
class GetTransferByIdQueryHandler(QueryHandler[GetTransferByIdQuery, dict]):
    def __init__(self, repo: Repository[StockTransfer]):
        self.repo = repo

    def _handle(self, query: GetTransferByIdQuery) -> dict:
        transfer = self.repo.get_by_id(query.id)
        if transfer is None:
            raise NotFoundError(f"StockTransfer with id {query.id} not found")
        return transfer.dict()


@dataclass
class GetTransferItemsQuery(Query):
    transfer_id: int = 0


@injectable(lifetime="scoped")
class GetTransferItemsQueryHandler(QueryHandler[GetTransferItemsQuery, list[dict]]):
    def __init__(self, item_repo: Repository[StockTransferItem]):
        self.item_repo = item_repo

    def _handle(self, query: GetTransferItemsQuery) -> list[dict]:
        items = self.item_repo.filter_by(transfer_id=query.transfer_id)
        return [item.dict() for item in items]
