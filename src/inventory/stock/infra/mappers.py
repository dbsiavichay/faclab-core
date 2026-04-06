from wireup import injectable

from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.models import StockModel
from src.shared.infra.mappers import Mapper


@injectable(lifetime="singleton")
class StockMapper(Mapper[Stock, StockModel]):
    __entity__ = Stock
