from datetime import date, timedelta
from typing import Any

from src.inventory.lot.domain.entities import Lot
from src.shared.domain.specifications import Specification


class LotsByProduct(Specification):
    def __init__(self, product_id: int):
        self.product_id = product_id

    def is_satisfied_by(self, candidate: Lot) -> bool:
        return candidate.product_id == self.product_id

    def to_query_criteria(self) -> list[Any]:
        from src.inventory.lot.infra.models import LotModel

        return [LotModel.product_id == self.product_id]


class ExpiringLots(Specification):
    def __init__(self, days: int = 30):
        self.days = days

    def is_satisfied_by(self, candidate: Lot) -> bool:
        if candidate.expiration_date is None:
            return False
        cutoff = date.today() + timedelta(days=self.days)
        return candidate.expiration_date <= cutoff and candidate.current_quantity > 0

    def to_query_criteria(self) -> list[Any]:
        from src.inventory.lot.infra.models import LotModel

        cutoff = date.today() + timedelta(days=self.days)
        return [
            LotModel.expiration_date <= cutoff,
            LotModel.current_quantity > 0,
            LotModel.expiration_date.isnot(None),
        ]


class ExpiredLots(Specification):
    def is_satisfied_by(self, candidate: Lot) -> bool:
        if candidate.expiration_date is None:
            return False
        return candidate.expiration_date < date.today()

    def to_query_criteria(self) -> list[Any]:
        from src.inventory.lot.infra.models import LotModel

        return [
            LotModel.expiration_date < date.today(),
            LotModel.expiration_date.isnot(None),
        ]
