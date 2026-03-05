from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.warehouse.app.commands.create import (
    CreateWarehouseCommand,
    CreateWarehouseCommandHandler,
)
from src.inventory.warehouse.app.commands.delete import (
    DeleteWarehouseCommand,
    DeleteWarehouseCommandHandler,
)
from src.inventory.warehouse.app.commands.update import (
    UpdateWarehouseCommand,
    UpdateWarehouseCommandHandler,
)
from src.inventory.warehouse.app.queries.get_warehouse import (
    GetAllWarehousesQuery,
    GetAllWarehousesQueryHandler,
    GetWarehouseByIdQuery,
    GetWarehouseByIdQueryHandler,
)
from src.inventory.warehouse.infra.validators import WarehouseRequest, WarehouseResponse
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, ListResponse, Meta


class WarehouseRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[WarehouseResponse],
            summary="Create warehouse",
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[WarehouseResponse],
            summary="Update warehouse",
        )(self.update)
        self.router.delete("/{id}", summary="Delete warehouse")(self.delete)
        self.router.get(
            "",
            response_model=ListResponse[WarehouseResponse],
            summary="Get all warehouses",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[WarehouseResponse],
            summary="Get warehouse by ID",
        )(self.get_by_id)

    def create(
        self,
        body: WarehouseRequest,
        handler: Injected[CreateWarehouseCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[WarehouseResponse]:
        result = handler.handle(
            CreateWarehouseCommand(**body.model_dump(by_alias=False))
        )
        return DataResponse(data=WarehouseResponse.model_validate(result), meta=meta)

    def update(
        self,
        id: int,
        body: WarehouseRequest,
        handler: Injected[UpdateWarehouseCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[WarehouseResponse]:
        result = handler.handle(
            UpdateWarehouseCommand(warehouse_id=id, **body.model_dump(by_alias=False))
        )
        return DataResponse(data=WarehouseResponse.model_validate(result), meta=meta)

    def delete(self, id: int, handler: Injected[DeleteWarehouseCommandHandler]) -> None:
        handler.handle(DeleteWarehouseCommand(warehouse_id=id))

    def get_all(
        self,
        handler: Injected[GetAllWarehousesQueryHandler],
        is_active: bool | None = None,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[WarehouseResponse]:
        result = handler.handle(GetAllWarehousesQuery(is_active=is_active))
        return ListResponse(
            data=[WarehouseResponse.model_validate(w) for w in result], meta=meta
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetWarehouseByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[WarehouseResponse]:
        result = handler.handle(GetWarehouseByIdQuery(warehouse_id=id))
        return DataResponse(data=WarehouseResponse.model_validate(result), meta=meta)
