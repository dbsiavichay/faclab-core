from fastapi import APIRouter, Query
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
    GetSerialsByProductQuery,
    GetSerialsByProductQueryHandler,
)
from src.inventory.serial.infra.validators import (
    SerialNumberRequest,
    SerialNumberResponse,
    SerialStatusUpdateRequest,
)


class SerialRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=SerialNumberResponse,
            summary="Create serial number",
        )(self.create)
        self.router.get(
            "",
            response_model=list[SerialNumberResponse],
            summary="Get serial numbers",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=SerialNumberResponse,
            summary="Get serial number by ID",
        )(self.get_by_id)
        self.router.put(
            "/{id}/status",
            response_model=SerialNumberResponse,
            summary="Update serial number status",
        )(self.update_status)

    def create(
        self,
        handler: Injected[CreateSerialNumberCommandHandler],
        body: SerialNumberRequest,
    ) -> SerialNumberResponse:
        """Creates a new serial number."""
        result = handler.handle(
            CreateSerialNumberCommand(**body.model_dump(exclude_none=True))
        )
        return SerialNumberResponse.model_validate(result)

    def get_all(
        self,
        handler: Injected[GetSerialsByProductQueryHandler],
        product_id: int | None = Query(None, description="Filter by product ID"),
        status: str | None = Query(None, description="Filter by status"),
    ) -> list[SerialNumberResponse]:
        """Retrieves serial numbers with optional filtering."""
        if product_id is not None:
            result = handler.handle(
                GetSerialsByProductQuery(product_id=product_id, status=status)
            )
        else:
            result = []
        return [SerialNumberResponse.model_validate(s) for s in result]

    def get_by_id(
        self,
        handler: Injected[GetSerialByIdQueryHandler],
        id: int,
    ) -> SerialNumberResponse:
        """Retrieves a serial number by ID."""
        result = handler.handle(GetSerialByIdQuery(id=id))
        return SerialNumberResponse.model_validate(result)

    def update_status(
        self,
        handler: Injected[UpdateSerialStatusCommandHandler],
        id: int,
        body: SerialStatusUpdateRequest,
    ) -> SerialNumberResponse:
        """Updates the status of a serial number."""
        result = handler.handle(UpdateSerialStatusCommand(id=id, status=body.status))
        return SerialNumberResponse.model_validate(result)
