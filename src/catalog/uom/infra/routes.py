from fastapi import APIRouter
from wireup import Injected

from src.catalog.uom.app.commands.create import (
    CreateUnitOfMeasureCommand,
    CreateUnitOfMeasureCommandHandler,
)
from src.catalog.uom.app.commands.delete import (
    DeleteUnitOfMeasureCommand,
    DeleteUnitOfMeasureCommandHandler,
)
from src.catalog.uom.app.commands.update import (
    UpdateUnitOfMeasureCommand,
    UpdateUnitOfMeasureCommandHandler,
)
from src.catalog.uom.app.queries.get_uom import (
    GetAllUnitsOfMeasureQuery,
    GetAllUnitsOfMeasureQueryHandler,
    GetUnitOfMeasureByIdQuery,
    GetUnitOfMeasureByIdQueryHandler,
)
from src.catalog.uom.infra.validators import UnitOfMeasureRequest, UnitOfMeasureResponse


class UnitOfMeasureRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "", response_model=UnitOfMeasureResponse, summary="Create unit of measure"
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=UnitOfMeasureResponse,
            summary="Update unit of measure",
        )(self.update)
        self.router.delete("/{id}", summary="Delete unit of measure")(self.delete)
        self.router.get(
            "",
            response_model=list[UnitOfMeasureResponse],
            summary="Get all units of measure",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=UnitOfMeasureResponse,
            summary="Get unit of measure by ID",
        )(self.get_by_id)

    def create(
        self,
        body: UnitOfMeasureRequest,
        handler: Injected[CreateUnitOfMeasureCommandHandler],
    ) -> UnitOfMeasureResponse:
        result = handler.handle(
            CreateUnitOfMeasureCommand(**body.model_dump(by_alias=False))
        )
        return UnitOfMeasureResponse.model_validate(result)

    def update(
        self,
        id: int,
        body: UnitOfMeasureRequest,
        handler: Injected[UpdateUnitOfMeasureCommandHandler],
    ) -> UnitOfMeasureResponse:
        result = handler.handle(
            UpdateUnitOfMeasureCommand(uom_id=id, **body.model_dump(by_alias=False))
        )
        return UnitOfMeasureResponse.model_validate(result)

    def delete(
        self, id: int, handler: Injected[DeleteUnitOfMeasureCommandHandler]
    ) -> None:
        handler.handle(DeleteUnitOfMeasureCommand(uom_id=id))

    def get_all(
        self,
        handler: Injected[GetAllUnitsOfMeasureQueryHandler],
        is_active: bool | None = None,
    ) -> list[UnitOfMeasureResponse]:
        result = handler.handle(GetAllUnitsOfMeasureQuery(is_active=is_active))
        return [UnitOfMeasureResponse.model_validate(u) for u in result]

    def get_by_id(
        self, id: int, handler: Injected[GetUnitOfMeasureByIdQueryHandler]
    ) -> UnitOfMeasureResponse:
        result = handler.handle(GetUnitOfMeasureByIdQuery(uom_id=id))
        return UnitOfMeasureResponse.model_validate(result)
