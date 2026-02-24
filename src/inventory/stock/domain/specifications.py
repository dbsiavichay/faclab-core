from typing import Any

from src.inventory.stock.domain.entities import Stock
from src.shared.domain.specifications import Specification


class LowStockProducts(Specification):
    def __init__(self, warehouse_id: int | None = None):
        self.warehouse_id = warehouse_id

    def is_satisfied_by(self, candidate: Stock) -> bool:
        # Cannot evaluate without product min_stock data
        return False

    def to_sql_criteria(self) -> list[Any]:
        from sqlalchemy import select

        from src.catalog.product.infra.models import ProductModel
        from src.inventory.location.infra.models import LocationModel
        from src.inventory.stock.infra.models import StockModel

        min_stock_subq = (
            select(ProductModel.min_stock)
            .where(ProductModel.id == StockModel.product_id)
            .scalar_subquery()
        )
        criteria: list[Any] = [
            StockModel.quantity <= min_stock_subq,
            StockModel.quantity > 0,
        ]
        if self.warehouse_id is not None:
            location_subq = select(LocationModel.id).where(
                LocationModel.warehouse_id == self.warehouse_id
            )
            criteria.append(StockModel.location_id.in_(location_subq))
        return criteria


class OutOfStockProducts(Specification):
    def __init__(self, warehouse_id: int | None = None):
        self.warehouse_id = warehouse_id

    def is_satisfied_by(self, candidate: Stock) -> bool:
        return candidate.quantity == 0

    def to_sql_criteria(self) -> list[Any]:
        from sqlalchemy import select

        from src.inventory.location.infra.models import LocationModel
        from src.inventory.stock.infra.models import StockModel

        criteria: list[Any] = [StockModel.quantity == 0]
        if self.warehouse_id is not None:
            location_subq = select(LocationModel.id).where(
                LocationModel.warehouse_id == self.warehouse_id
            )
            criteria.append(StockModel.location_id.in_(location_subq))
        return criteria


class ReorderPointProducts(Specification):
    def __init__(self, warehouse_id: int | None = None):
        self.warehouse_id = warehouse_id

    def is_satisfied_by(self, candidate: Stock) -> bool:
        # Cannot evaluate without product reorder_point data
        return False

    def to_sql_criteria(self) -> list[Any]:
        from sqlalchemy import select

        from src.catalog.product.infra.models import ProductModel
        from src.inventory.location.infra.models import LocationModel
        from src.inventory.stock.infra.models import StockModel

        reorder_point_subq = (
            select(ProductModel.reorder_point)
            .where(ProductModel.id == StockModel.product_id)
            .scalar_subquery()
        )
        criteria: list[Any] = [
            StockModel.quantity <= reorder_point_subq,
            StockModel.quantity > 0,
        ]
        if self.warehouse_id is not None:
            location_subq = select(LocationModel.id).where(
                LocationModel.warehouse_id == self.warehouse_id
            )
            criteria.append(StockModel.location_id.in_(location_subq))
        return criteria
