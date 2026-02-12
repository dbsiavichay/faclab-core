from typing import Any

from wireup import injectable

from src.sales.domain.entities import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    Sale,
    SaleItem,
    SaleStatus,
)
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.infra.mappers import Mapper


@injectable
class SaleMapper(Mapper[Sale, SaleModel]):
    """Mapper para convertir entre Sale entity y SaleModel"""

    def to_entity(self, model: SaleModel | None) -> Sale | None:
        """Convierte un modelo de infraestructura a una entidad de dominio"""
        if not model:
            return None

        return Sale(
            id=model.id,
            customer_id=model.customer_id,
            status=SaleStatus(model.status),
            sale_date=model.sale_date,
            subtotal=model.subtotal,
            tax=model.tax,
            discount=model.discount,
            total=model.total,
            payment_status=PaymentStatus(model.payment_status),
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_dict(self, entity: Sale) -> dict[str, Any]:
        """Convierte una entidad de dominio a un diccionario para crear un modelo"""
        result = {
            "customer_id": entity.customer_id,
            "status": entity.status.value,
            "sale_date": entity.sale_date,
            "subtotal": entity.subtotal,
            "tax": entity.tax,
            "discount": entity.discount,
            "total": entity.total,
            "payment_status": entity.payment_status.value,
            "notes": entity.notes,
            "created_by": entity.created_by,
        }

        # Only include id if it's not None
        if entity.id is not None:
            result["id"] = entity.id

        # Include timestamps if they exist
        if entity.created_at is not None:
            result["created_at"] = entity.created_at
        if entity.updated_at is not None:
            result["updated_at"] = entity.updated_at

        return result


@injectable
class SaleItemMapper(Mapper[SaleItem, SaleItemModel]):
    """Mapper para convertir entre SaleItem entity y SaleItemModel"""

    def to_entity(self, model: SaleItemModel | None) -> SaleItem | None:
        """Convierte un modelo de infraestructura a una entidad de dominio"""
        if not model:
            return None

        return SaleItem(
            id=model.id,
            sale_id=model.sale_id,
            product_id=model.product_id,
            quantity=model.quantity,
            unit_price=model.unit_price,
            discount=model.discount,
        )

    def to_dict(self, entity: SaleItem) -> dict[str, Any]:
        """Convierte una entidad de dominio a un diccionario para crear un modelo"""
        result = {
            "sale_id": entity.sale_id,
            "product_id": entity.product_id,
            "quantity": entity.quantity,
            "unit_price": entity.unit_price,
            "discount": entity.discount,
        }

        # Only include id if it's not None
        if entity.id is not None:
            result["id"] = entity.id

        return result


@injectable
class PaymentMapper(Mapper[Payment, PaymentModel]):
    """Mapper para convertir entre Payment entity y PaymentModel"""

    def to_entity(self, model: PaymentModel | None) -> Payment | None:
        """Convierte un modelo de infraestructura a una entidad de dominio"""
        if not model:
            return None

        return Payment(
            id=model.id,
            sale_id=model.sale_id,
            amount=model.amount,
            payment_method=PaymentMethod(model.payment_method),
            payment_date=model.payment_date,
            reference=model.reference,
            notes=model.notes,
            created_at=model.created_at,
        )

    def to_dict(self, entity: Payment) -> dict[str, Any]:
        """Convierte una entidad de dominio a un diccionario para crear un modelo"""
        result = {
            "sale_id": entity.sale_id,
            "amount": entity.amount,
            "payment_method": entity.payment_method.value,
            "payment_date": entity.payment_date,
            "reference": entity.reference,
            "notes": entity.notes,
        }

        # Only include id if it's not None
        if entity.id is not None:
            result["id"] = entity.id

        # Include timestamp if it exists
        if entity.created_at is not None:
            result["created_at"] = entity.created_at

        return result
