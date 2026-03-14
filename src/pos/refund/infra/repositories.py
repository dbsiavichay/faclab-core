from sqlalchemy.orm import Session
from wireup import injectable

from src.pos.refund.domain.entities import Refund, RefundItem, RefundPayment
from src.pos.refund.infra.mappers import (
    RefundItemMapper,
    RefundMapper,
    RefundPaymentMapper,
)
from src.pos.refund.infra.models import RefundItemModel, RefundModel, RefundPaymentModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[Refund])
class RefundRepository(SqlAlchemyRepository[Refund]):
    __model__ = RefundModel

    def __init__(self, session: Session, mapper: RefundMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[RefundItem])
class RefundItemRepository(SqlAlchemyRepository[RefundItem]):
    __model__ = RefundItemModel

    def __init__(self, session: Session, mapper: RefundItemMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[RefundPayment])
class RefundPaymentRepository(SqlAlchemyRepository[RefundPayment]):
    __model__ = RefundPaymentModel

    def __init__(self, session: Session, mapper: RefundPaymentMapper):
        super().__init__(session, mapper)
