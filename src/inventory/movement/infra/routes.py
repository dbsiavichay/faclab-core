from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.movement.infra.validators import (
    MovementInput,
    MovementQueryParams,
    MovementResponse,
)

from .controllers import MovementController


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
        new_movement: MovementInput,
        movement_controller: Injected[MovementController],
    ) -> MovementResponse:
        """Save a new movement."""
        return movement_controller.create(new_movement)

    def get_all(
        self,
        movement_controller: Injected[MovementController],
        query_params: MovementQueryParams = Depends(),
    ) -> list[MovementResponse]:
        """Get all movements."""
        return movement_controller.get_all(query_params)
