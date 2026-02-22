from fastapi import APIRouter
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


class WarehouseRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "", response_model=WarehouseResponse, summary="Create warehouse"
        )(self.create)
        self.router.put(
            "/{id}", response_model=WarehouseResponse, summary="Update warehouse"
        )(self.update)
        self.router.delete("/{id}", summary="Delete warehouse")(self.delete)
        self.router.get(
            "",
            response_model=list[WarehouseResponse],
            summary="Get all warehouses",
        )(self.get_all)
        self.router.get(
            "/{id}", response_model=WarehouseResponse, summary="Get warehouse by ID"
        )(self.get_by_id)

    def create(
        self,
        body: WarehouseRequest,
        handler: Injected[CreateWarehouseCommandHandler],
    ) -> WarehouseResponse:
        result = handler.handle(
            CreateWarehouseCommand(**body.model_dump(by_alias=False))
        )
        return WarehouseResponse.model_validate(result)

    def update(
        self,
        id: int,
        body: WarehouseRequest,
        handler: Injected[UpdateWarehouseCommandHandler],
    ) -> WarehouseResponse:
        result = handler.handle(
            UpdateWarehouseCommand(warehouse_id=id, **body.model_dump(by_alias=False))
        )
        return WarehouseResponse.model_validate(result)

    def delete(self, id: int, handler: Injected[DeleteWarehouseCommandHandler]) -> None:
        handler.handle(DeleteWarehouseCommand(warehouse_id=id))

    def get_all(
        self,
        handler: Injected[GetAllWarehousesQueryHandler],
        is_active: bool | None = None,
    ) -> list[WarehouseResponse]:
        result = handler.handle(GetAllWarehousesQuery(is_active=is_active))
        return [WarehouseResponse.model_validate(w) for w in result]

    def get_by_id(
        self, id: int, handler: Injected[GetWarehouseByIdQueryHandler]
    ) -> WarehouseResponse:
        result = handler.handle(GetWarehouseByIdQuery(warehouse_id=id))
        return WarehouseResponse.model_validate(result)
