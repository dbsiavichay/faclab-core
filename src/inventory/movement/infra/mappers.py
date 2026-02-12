from typing import Any

from wireup import injectable

from src.inventory.movement.domain.entities import Movement
from src.shared.infra.mappers import Mapper

from .models import MovementModel


@injectable  # Singleton by default (stateless mapper)
class MovementMapper(Mapper[MovementModel, Movement]):
    def to_entity(self, model: MovementModel | None) -> Movement | None:
        """Converts an infrastructure model to a domain entity"""
        if model is None:
            return None

        return Movement(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            type=model.type,
            reason=model.reason,
            date=model.date,
        )

    def to_dict(self, entity: Movement) -> dict[str, Any]:
        """Converts a domain entity to a dictionary for creating a model"""
        result = {
            "product_id": entity.product_id,
            "quantity": entity.quantity,
            "type": entity.type,
            "reason": entity.reason,
            "date": entity.date,
        }

        if entity.id:
            result["id"] = entity.id
        return result
