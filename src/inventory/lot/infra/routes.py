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
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import (
    RESPONSES_COMMAND,
    RESPONSES_LIST,
    RESPONSES_QUERY,
    DataResponse,
    Meta,
    PaginatedDataResponse,
)


class LotRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[LotResponse],
            summary="Create lot",
            responses=RESPONSES_COMMAND,
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[LotResponse],
            summary="Update lot",
            responses=RESPONSES_COMMAND,
        )(self.update)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[LotResponse],
            summary="Get lots",
            responses=RESPONSES_LIST,
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[LotResponse],
            summary="Get lot by ID",
            responses=RESPONSES_QUERY,
        )(self.get_by_id)

    def create(
        self,
        handler: Injected[CreateLotCommandHandler],
        body: LotRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LotResponse]:
        """Creates a new lot."""
        result = handler.handle(CreateLotCommand(**body.model_dump(exclude_none=True)))
        return DataResponse(data=LotResponse.model_validate(result), meta=meta)

    def update(
        self,
        handler: Injected[UpdateLotCommandHandler],
        id: int,
        body: LotUpdateRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LotResponse]:
        """Updates a lot."""
        result = handler.handle(
            UpdateLotCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return DataResponse(data=LotResponse.model_validate(result), meta=meta)

    def get_all(
        self,
        handler: Injected[GetAllLotsQueryHandler],
        query_params: LotQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[LotResponse]:
        """Retrieves lots with optional filtering."""
        result = handler.handle(
            GetAllLotsQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[LotResponse.model_validate(lot) for lot in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        handler: Injected[GetLotByIdQueryHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LotResponse]:
        """Retrieves a lot by ID."""
        result = handler.handle(GetLotByIdQuery(id=id))
        return DataResponse(data=LotResponse.model_validate(result), meta=meta)
