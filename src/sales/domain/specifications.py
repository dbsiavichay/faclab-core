"""Especificaciones del dominio de Sales"""

from typing import Any

from src.shared.domain.specifications import Specification


class ParkedSalesSpecification(Specification):
    """Especificacion para ventas aparcadas (DRAFT con parked_at no nulo)"""

    def is_satisfied_by(self, candidate: Any) -> bool:
        return candidate.status == "DRAFT" and candidate.parked_at is not None

    def to_query_criteria(self) -> list[Any]:
        from src.sales.infra.models import SaleModel

        return [
            SaleModel.status == "DRAFT",
            SaleModel.parked_at.isnot(None),
        ]
