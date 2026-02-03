from typing import List

from src.inventory.movement.app.types import MovementInput, MovementOutput
from src.inventory.movement.domain.entities import Movement
from src.inventory.stock.domain.entities import Stock
from src.shared.app.repositories import Repository


class CreateMovementUseCase:
    def __init__(
        self, movement_repo: Repository[Movement], stock_repo: Repository[Stock]
    ):
        self.movement_repo = movement_repo
        self.stock_repo = stock_repo

    def execute(self, movement_create: MovementInput) -> MovementOutput:
        movement = Movement(**movement_create)
        movement = self.movement_repo.create(movement)
        stock = self.stock_repo.first(product_id=movement.product_id)
        if stock is None:
            stock = Stock(product_id=movement.product_id, quantity=movement.quantity)
            self.stock_repo.create(stock)
        else:
            stock.update_quantity(movement.quantity)
            self.stock_repo.update(stock)
        return movement.dict()


class FilterMovementsUseCase:
    def __init__(self, movement_repo: Repository[Movement]):
        self.movement_repo = movement_repo

    def execute(self, **params) -> List[MovementOutput]:
        movements = self.movement_repo.filter_by(**params)
        return [movement.dict() for movement in movements]
