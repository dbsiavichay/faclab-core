from wireup import injectable

from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.infra.mappers import Mapper


@injectable
class SaleMapper(Mapper[Sale, SaleModel]):
    __entity__ = Sale
    __exclude_fields__ = frozenset({"created_at", "updated_at"})


@injectable
class SaleItemMapper(Mapper[SaleItem, SaleItemModel]):
    __entity__ = SaleItem


@injectable
class PaymentMapper(Mapper[Payment, PaymentModel]):
    __entity__ = Payment
    __exclude_fields__ = frozenset({"created_at"})
