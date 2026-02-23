from fastapi import APIRouter, Query
from wireup import Injected

from src.inventory.lot.app.commands.lot import (
    CreateLotCommand,
    CreateLotCommandHandler,
    UpdateLotCommand,
    UpdateLotCommandHandler,
)
from src.inventory.lot.app.queries.lot import (
    GetExpiringLotsQuery,
    GetExpiringLotsQueryHandler,
    GetLotByIdQuery,
    GetLotByIdQueryHandler,
    GetLotsByProductQuery,
    GetLotsByProductQueryHandler,
)
from src.inventory.lot.infra.validators import LotRequest, LotResponse, LotUpdateRequest


class LotRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=LotResponse,
            summary="Create lot",
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=LotResponse,
            summary="Update lot",
        )(self.update)
        self.router.get(
            "",
            response_model=list[LotResponse],
            summary="Get lots",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=LotResponse,
            summary="Get lot by ID",
        )(self.get_by_id)

    def create(
        self,
        handler: Injected[CreateLotCommandHandler],
        body: LotRequest,
    ) -> LotResponse:
        """Creates a new lot."""
        result = handler.handle(CreateLotCommand(**body.model_dump(exclude_none=True)))
        return LotResponse.model_validate(result)

    def update(
        self,
        handler: Injected[UpdateLotCommandHandler],
        id: int,
        body: LotUpdateRequest,
    ) -> LotResponse:
        """Updates a lot."""
        result = handler.handle(
            UpdateLotCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return LotResponse.model_validate(result)

    def get_all(
        self,
        handler: Injected[GetLotsByProductQueryHandler],
        expiring_handler: Injected[GetExpiringLotsQueryHandler],
        product_id: int | None = Query(None, description="Filter by product ID"),
        expiring_in_days: int | None = Query(
            None, description="Return lots expiring within this many days"
        ),
    ) -> list[LotResponse]:
        """Retrieves lots with optional filtering. Use product_id or expiring_in_days."""
        if expiring_in_days is not None:
            result = expiring_handler.handle(
                GetExpiringLotsQuery(days=expiring_in_days)
            )
            if product_id is not None:
                result = [r for r in result if r["product_id"] == product_id]
        elif product_id is not None:
            result = handler.handle(GetLotsByProductQuery(product_id=product_id))
        else:
            result = []
        return [LotResponse.model_validate(lot) for lot in result]

    def get_by_id(
        self,
        handler: Injected[GetLotByIdQueryHandler],
        id: int,
    ) -> LotResponse:
        """Retrieves a lot by ID."""
        result = handler.handle(GetLotByIdQuery(id=id))
        return LotResponse.model_validate(result)
