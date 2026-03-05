from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.lot.app.commands.lot import (
    CreateLotCommand,
    CreateLotCommandHandler,
    UpdateLotCommand,
    UpdateLotCommandHandler,
)
from src.inventory.lot.app.queries.lot import (
    GetAllLotsQuery,
    GetAllLotsQueryHandler,
    GetLotByIdQuery,
    GetLotByIdQueryHandler,
)
from src.inventory.lot.infra.validators import (
    LotQueryParams,
    LotRequest,
    LotResponse,
    LotUpdateRequest,
)
from src.shared.infra.validators import PaginatedResponse


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
            response_model=PaginatedResponse[LotResponse],
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
        handler: Injected[GetAllLotsQueryHandler],
        query_params: LotQueryParams = Depends(),
    ) -> PaginatedResponse[LotResponse]:
        """Retrieves lots with optional filtering."""
        result = handler.handle(
            GetAllLotsQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedResponse[LotResponse](
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            items=[LotResponse.model_validate(lot) for lot in result["items"]],
        )

    def get_by_id(
        self,
        handler: Injected[GetLotByIdQueryHandler],
        id: int,
    ) -> LotResponse:
        """Retrieves a lot by ID."""
        result = handler.handle(GetLotByIdQuery(id=id))
        return LotResponse.model_validate(result)
