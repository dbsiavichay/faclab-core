from sqlalchemy.orm import Session
from wireup import injectable

from src.pos.refund.app.repositories import (
    RefundItemRepository,
    RefundPaymentRepository,
    RefundRepository,
)
from src.pos.refund.domain.entities import Refund, RefundItem, RefundPayment
from src.pos.refund.infra.mappers import (
    RefundItemMapper,
    RefundMapper,
    RefundPaymentMapper,
)
from src.pos.refund.infra.models import RefundItemModel, RefundModel, RefundPaymentModel
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=RefundRepository)
class SqlAlchemyRefundRepository(SqlAlchemyRepository[Refund], RefundRepository):
    __model__ = RefundModel

    def __init__(self, session: Session, mapper: RefundMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=RefundItemRepository)
class SqlAlchemyRefundItemRepository(
    SqlAlchemyRepository[RefundItem], RefundItemRepository
):
    __model__ = RefundItemModel

    def __init__(self, session: Session, mapper: RefundItemMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=RefundPaymentRepository)
class SqlAlchemyRefundPaymentRepository(
    SqlAlchemyRepository[RefundPayment], RefundPaymentRepository
):
    __model__ = RefundPaymentModel

    def __init__(self, session: Session, mapper: RefundPaymentMapper):
        super().__init__(session, mapper)
