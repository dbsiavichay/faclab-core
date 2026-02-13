from dataclasses import dataclass

from wireup import injectable

from src.inventory.stock.domain.entities import Stock
from src.shared.app.queries import Query, QueryHandler
from src.shared.app.repositories import Repository


@dataclass
class GetAllStocksQuery(Query):
    """Query para obtener todos los stocks con filtros opcionales"""

    product_id: int | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class GetAllStocksQueryHandler(QueryHandler[GetAllStocksQuery, list[dict]]):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def _handle(self, query: GetAllStocksQuery) -> list[dict]:
        # Build filter kwargs
        filter_kwargs = {}
        if query.product_id is not None:
            filter_kwargs["product_id"] = query.product_id

        # Apply pagination
        stocks = self.repo.filter_by(
            limit=query.limit, offset=query.offset, **filter_kwargs
        )
        return [stock.dict() for stock in stocks]


@dataclass
class GetStockByIdQuery(Query):
    """Query para obtener un stock por su ID"""

    id: int = 0


@injectable(lifetime="scoped")
class GetStockByIdQueryHandler(QueryHandler[GetStockByIdQuery, dict | None]):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def _handle(self, query: GetStockByIdQuery) -> dict | None:
        stock = self.repo.get_by_id(query.id)
        if stock is None:
            return None
        return stock.dict()


@dataclass
class GetStockByProductQuery(Query):
    """Query para obtener el stock de un producto específico"""

    product_id: int = 0


@injectable(lifetime="scoped")
class GetStockByProductQueryHandler(QueryHandler[GetStockByProductQuery, dict | None]):
    def __init__(self, repo: Repository[Stock]):
        self.repo = repo

    def _handle(self, query: GetStockByProductQuery) -> dict | None:
        stock = self.repo.first(product_id=query.product_id)
        if stock is None:
            return None
        return stock.dict()
