from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.serial.app.commands.serial import (
    CreateSerialNumberCommand,
    CreateSerialNumberCommandHandler,
    UpdateSerialStatusCommand,
    UpdateSerialStatusCommandHandler,
)
from src.inventory.serial.app.queries.serial import (
    GetSerialByIdQuery,
    GetSerialByIdQueryHandler,
    GetSerialsQuery,
    GetSerialsQueryHandler,
)
from src.inventory.serial.infra.validators import (
    SerialNumberRequest,
    SerialNumberResponse,
    SerialQueryParams,
    SerialStatusUpdateRequest,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, Meta, PaginatedDataResponse


class SerialRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[SerialNumberResponse],
            summary="Create serial number",
        )(self.create)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[SerialNumberResponse],
            summary="Get serial numbers",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[SerialNumberResponse],
            summary="Get serial number by ID",
        )(self.get_by_id)
        self.router.put(
            "/{id}/status",
            response_model=DataResponse[SerialNumberResponse],
            summary="Update serial number status",
        )(self.update_status)

    def create(
        self,
        handler: Injected[CreateSerialNumberCommandHandler],
        body: SerialNumberRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SerialNumberResponse]:
        """Creates a new serial number."""
        result = handler.handle(
            CreateSerialNumberCommand(**body.model_dump(exclude_none=True))
        )
        return DataResponse(data=SerialNumberResponse.model_validate(result), meta=meta)

    def get_all(
        self,
        handler: Injected[GetSerialsQueryHandler],
        query_params: SerialQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[SerialNumberResponse]:
        """Retrieves serial numbers with optional filtering."""
        result = handler.handle(
            GetSerialsQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[SerialNumberResponse.model_validate(s) for s in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        handler: Injected[GetSerialByIdQueryHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SerialNumberResponse]:
        """Retrieves a serial number by ID."""
        result = handler.handle(GetSerialByIdQuery(id=id))
        return DataResponse(data=SerialNumberResponse.model_validate(result), meta=meta)

    def update_status(
        self,
        handler: Injected[UpdateSerialStatusCommandHandler],
        id: int,
        body: SerialStatusUpdateRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SerialNumberResponse]:
        """Updates the status of a serial number."""
        result = handler.handle(UpdateSerialStatusCommand(id=id, status=body.status))
        return DataResponse(data=SerialNumberResponse.model_validate(result), meta=meta)
