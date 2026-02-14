from sqlalchemy.orm import Session
from wireup import injectable

from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Sale])
class SaleRepository(SqlAlchemyRepository[Sale]):
    __model__ = SaleModel

    def __init__(self, session: Session, mapper: SaleMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[SaleItem])
class SaleItemRepository(SqlAlchemyRepository[SaleItem]):
    __model__ = SaleItemModel

    def __init__(self, session: Session, mapper: SaleItemMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[Payment])
class PaymentRepository(SqlAlchemyRepository[Payment]):
    __model__ = PaymentModel

    def __init__(self, session: Session, mapper: PaymentMapper):
        super().__init__(session, mapper)
