from wireup import injectable

from src.inventory.movement.app.commands import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.app.queries import (
    GetAllMovementsQuery,
    GetAllMovementsQueryHandler,
    GetMovementByIdQuery,
    GetMovementByIdQueryHandler,
)
from src.shared.infra.exceptions import NotFoundError

from .validators import MovementInput, MovementQueryParams, MovementResponse


@injectable(lifetime="scoped")
class MovementController:
    def __init__(
        self,
        create_handler: CreateMovementCommandHandler,
        get_all_handler: GetAllMovementsQueryHandler,
        get_by_id_handler: GetMovementByIdQueryHandler,
    ):
        self.create_handler = create_handler
        self.get_all_handler = get_all_handler
        self.get_by_id_handler = get_by_id_handler

    def create(self, new_movement: MovementInput) -> MovementResponse:
        command = CreateMovementCommand(**new_movement.model_dump(exclude_none=True))
        result = self.create_handler.handle(command)
        return MovementResponse.model_validate(result)

    def get_all(self, query_params: MovementQueryParams) -> list[MovementResponse]:
        query = GetAllMovementsQuery(**query_params.model_dump(exclude_none=True))
        movements = self.get_all_handler.handle(query)
        return [MovementResponse.model_validate(movement) for movement in movements]

    def get_by_id(self, id: int) -> MovementResponse:
        movement = self.get_by_id_handler.handle(GetMovementByIdQuery(id=id))
        if movement is None:
            raise NotFoundError("Movement not found")
        return MovementResponse.model_validate(movement)
