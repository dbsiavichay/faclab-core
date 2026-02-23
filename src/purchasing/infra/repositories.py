from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from wireup import injectable

from src.purchasing.domain.entities import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseReceiptItem,
)
from src.purchasing.infra.mappers import (
    PurchaseOrderItemMapper,
    PurchaseOrderMapper,
    PurchaseReceiptItemMapper,
    PurchaseReceiptMapper,
)
from src.purchasing.infra.models import (
    PurchaseOrderItemModel,
    PurchaseOrderModel,
    PurchaseReceiptItemModel,
    PurchaseReceiptModel,
)
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository


@injectable(lifetime="scoped", as_type=Repository[PurchaseOrder])
class PurchaseOrderRepository(SqlAlchemyRepository[PurchaseOrder]):
    __model__ = PurchaseOrderModel

    def __init__(self, session: Session, mapper: PurchaseOrderMapper):
        super().__init__(session, mapper)

    def count_by_year(self, year: int) -> int:
        return (
            self.session.query(func.count(self.__model__.id))
            .filter(extract("year", self.__model__.created_at) == year)
            .scalar()
            or 0
        )


@injectable(lifetime="scoped", as_type=Repository[PurchaseOrderItem])
class PurchaseOrderItemRepository(SqlAlchemyRepository[PurchaseOrderItem]):
    __model__ = PurchaseOrderItemModel

    def __init__(self, session: Session, mapper: PurchaseOrderItemMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[PurchaseReceipt])
class PurchaseReceiptRepository(SqlAlchemyRepository[PurchaseReceipt]):
    __model__ = PurchaseReceiptModel

    def __init__(self, session: Session, mapper: PurchaseReceiptMapper):
        super().__init__(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[PurchaseReceiptItem])
class PurchaseReceiptItemRepository(SqlAlchemyRepository[PurchaseReceiptItem]):
    __model__ = PurchaseReceiptItemModel

    def __init__(self, session: Session, mapper: PurchaseReceiptItemMapper):
        super().__init__(session, mapper)
