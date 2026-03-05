from fastapi import APIRouter, Depends
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
from src.catalog.uom.infra.validators import (
    UnitOfMeasureQueryParams,
    UnitOfMeasureRequest,
    UnitOfMeasureResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, Meta, PaginatedDataResponse


class UnitOfMeasureRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[UnitOfMeasureResponse],
            summary="Create unit of measure",
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[UnitOfMeasureResponse],
            summary="Update unit of measure",
        )(self.update)
        self.router.delete("/{id}", summary="Delete unit of measure")(self.delete)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[UnitOfMeasureResponse],
            summary="Get all units of measure",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[UnitOfMeasureResponse],
            summary="Get unit of measure by ID",
        )(self.get_by_id)

    def create(
        self,
        body: UnitOfMeasureRequest,
        handler: Injected[CreateUnitOfMeasureCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[UnitOfMeasureResponse]:
        result = handler.handle(
            CreateUnitOfMeasureCommand(**body.model_dump(by_alias=False))
        )
        return DataResponse(
            data=UnitOfMeasureResponse.model_validate(result), meta=meta
        )

    def update(
        self,
        id: int,
        body: UnitOfMeasureRequest,
        handler: Injected[UpdateUnitOfMeasureCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[UnitOfMeasureResponse]:
        result = handler.handle(
            UpdateUnitOfMeasureCommand(uom_id=id, **body.model_dump(by_alias=False))
        )
        return DataResponse(
            data=UnitOfMeasureResponse.model_validate(result), meta=meta
        )

    def delete(
        self, id: int, handler: Injected[DeleteUnitOfMeasureCommandHandler]
    ) -> None:
        handler.handle(DeleteUnitOfMeasureCommand(uom_id=id))

    def get_all(
        self,
        handler: Injected[GetAllUnitsOfMeasureQueryHandler],
        query_params: UnitOfMeasureQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[UnitOfMeasureResponse]:
        result = handler.handle(
            GetAllUnitsOfMeasureQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[UnitOfMeasureResponse.model_validate(u) for u in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetUnitOfMeasureByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[UnitOfMeasureResponse]:
        result = handler.handle(GetUnitOfMeasureByIdQuery(uom_id=id))
        return DataResponse(
            data=UnitOfMeasureResponse.model_validate(result), meta=meta
        )
