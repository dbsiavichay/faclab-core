from typing import List

from src.inventory.movement.app.use_cases import (
    CreateMovementUseCase,
    FilterMovementsUseCase,
)

from .validators import MovementInput, MovementQueryParams, MovementResponse


class MovementController:
    def __init__(
        self,
        create_movement: CreateMovementUseCase,
        filter_movements: FilterMovementsUseCase,
    ):
        self.create_movement = create_movement
        self.filter_movements = filter_movements

    def create(self, new_movement: MovementInput) -> MovementResponse:
        movement = self.create_movement.execute(
            new_movement.model_dump(exclude_none=True)
        )
        return MovementResponse.model_validate(movement)

    def get_all(self, query_params: MovementQueryParams) -> List[MovementResponse]:
        params = query_params.model_dump(exclude_none=True)
        movements = self.filter_movements.execute(**params)
        return [MovementResponse.model_validate(movement) for movement in movements]
