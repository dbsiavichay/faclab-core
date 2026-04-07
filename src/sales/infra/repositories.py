from sqlalchemy.orm import Session
from wireup import injectable

from src.sales.app.repositories import (
    PaymentRepository,
    SaleItemRepository,
    SaleRepository,
)
from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=SaleRepository)
class SqlAlchemySaleRepository(SqlAlchemyRepository[Sale], SaleRepository):
    __model__ = SaleModel

    def __init__(self, session: Session, mapper: SaleMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=SaleItemRepository)
class SqlAlchemySaleItemRepository(SqlAlchemyRepository[SaleItem], SaleItemRepository):
    __model__ = SaleItemModel

    def __init__(self, session: Session, mapper: SaleItemMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=PaymentRepository)
class SqlAlchemyPaymentRepository(SqlAlchemyRepository[Payment], PaymentRepository):
    __model__ = PaymentModel

    def __init__(self, session: Session, mapper: PaymentMapper):
        super().__init__(session, mapper)
