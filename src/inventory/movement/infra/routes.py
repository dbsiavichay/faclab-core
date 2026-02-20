from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.movement.app.commands.movement import (
    CreateMovementCommand,
    CreateMovementCommandHandler,
)
from src.inventory.movement.app.queries.movement import (
    GetAllMovementsQuery,
    GetAllMovementsQueryHandler,
)
from src.inventory.movement.infra.validators import (
    MovementQueryParams,
    MovementRequest,
    MovementResponse,
)


class MovementRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Sets up all the routes for the router."""
        self.router.post("", response_model=MovementResponse, summary="Save movement")(
            self.create
        )
        self.router.get(
            "", response_model=list[MovementResponse], summary="Get all movements"
        )(self.get_all)

    def create(
        self,
        new_movement: MovementRequest,
        handler: Injected[CreateMovementCommandHandler],
    ) -> MovementResponse:
        """Save a new movement."""
        result = handler.handle(
            CreateMovementCommand(**new_movement.model_dump(exclude_none=True))
        )
        return MovementResponse.model_validate(result)

    def get_all(
        self,
        handler: Injected[GetAllMovementsQueryHandler],
        query_params: MovementQueryParams = Depends(),
    ) -> list[MovementResponse]:
        """Get all movements."""
        result = handler.handle(
            GetAllMovementsQuery(**query_params.model_dump(exclude_none=True))
        )
        return [MovementResponse.model_validate(m) for m in result]
