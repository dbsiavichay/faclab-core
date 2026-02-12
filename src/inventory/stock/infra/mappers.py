from typing import Any

from wireup import injectable

from src.inventory.stock.domain.entities import Stock
from src.inventory.stock.infra.models import StockModel
from src.shared.infra.mappers import Mapper


@injectable  # Singleton by default (stateless mapper)
class StockMapper(Mapper[Stock, StockModel]):
    def to_entity(self, model: StockModel | None) -> Stock | None:
        """Converts an infrastructure model to a domain entity"""
        if model is None:
            return None

        return Stock(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            location=model.location,
        )

    def to_dict(self, entity: Stock) -> dict[str, Any]:
        """Converts a domain entity to a dictionary for creating a model"""
        result = {
            "product_id": entity.product_id,
            "quantity": entity.quantity,
            "location": entity.location,
        }

        # Only include these fields if they are not None
        if entity.id is not None:
            result["id"] = entity.id

        return result
