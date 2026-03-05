from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.location.app.commands.create import (
    CreateLocationCommand,
    CreateLocationCommandHandler,
)
from src.inventory.location.app.commands.delete import (
    DeleteLocationCommand,
    DeleteLocationCommandHandler,
)
from src.inventory.location.app.commands.update import (
    UpdateLocationCommand,
    UpdateLocationCommandHandler,
)
from src.inventory.location.app.queries.get_location import (
    GetAllLocationsQuery,
    GetAllLocationsQueryHandler,
    GetLocationByIdQuery,
    GetLocationByIdQueryHandler,
)
from src.inventory.location.infra.validators import LocationRequest, LocationResponse
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, ListResponse, Meta


class LocationRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[LocationResponse],
            summary="Create location",
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[LocationResponse],
            summary="Update location",
        )(self.update)
        self.router.delete("/{id}", summary="Delete location")(self.delete)
        self.router.get(
            "",
            response_model=ListResponse[LocationResponse],
            summary="Get all locations",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[LocationResponse],
            summary="Get location by ID",
        )(self.get_by_id)

    def create(
        self,
        body: LocationRequest,
        handler: Injected[CreateLocationCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LocationResponse]:
        result = handler.handle(
            CreateLocationCommand(**body.model_dump(by_alias=False))
        )
        return DataResponse(data=LocationResponse.model_validate(result), meta=meta)

    def update(
        self,
        id: int,
        body: LocationRequest,
        handler: Injected[UpdateLocationCommandHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LocationResponse]:
        result = handler.handle(
            UpdateLocationCommand(location_id=id, **body.model_dump(by_alias=False))
        )
        return DataResponse(data=LocationResponse.model_validate(result), meta=meta)

    def delete(self, id: int, handler: Injected[DeleteLocationCommandHandler]) -> None:
        handler.handle(DeleteLocationCommand(location_id=id))

    def get_all(
        self,
        handler: Injected[GetAllLocationsQueryHandler],
        warehouse_id: int | None = None,
        is_active: bool | None = None,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[LocationResponse]:
        result = handler.handle(
            GetAllLocationsQuery(warehouse_id=warehouse_id, is_active=is_active)
        )
        return ListResponse(
            data=[LocationResponse.model_validate(loc) for loc in result], meta=meta
        )

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetLocationByIdQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[LocationResponse]:
        result = handler.handle(GetLocationByIdQuery(location_id=id))
        return DataResponse(data=LocationResponse.model_validate(result), meta=meta)
