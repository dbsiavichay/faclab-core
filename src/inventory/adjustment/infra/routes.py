from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.adjustment.app.commands.adjustment import (
    AddAdjustmentItemCommand,
    AddAdjustmentItemCommandHandler,
    CancelAdjustmentCommand,
    CancelAdjustmentCommandHandler,
    ConfirmAdjustmentCommand,
    ConfirmAdjustmentCommandHandler,
    CreateAdjustmentCommand,
    CreateAdjustmentCommandHandler,
    DeleteAdjustmentCommand,
    DeleteAdjustmentCommandHandler,
    RemoveAdjustmentItemCommand,
    RemoveAdjustmentItemCommandHandler,
    UpdateAdjustmentCommand,
    UpdateAdjustmentCommandHandler,
    UpdateAdjustmentItemCommand,
    UpdateAdjustmentItemCommandHandler,
)
from src.inventory.adjustment.app.queries.adjustment import (
    GetAdjustmentByIdQuery,
    GetAdjustmentByIdQueryHandler,
    GetAdjustmentItemsQuery,
    GetAdjustmentItemsQueryHandler,
    GetAllAdjustmentsQuery,
    GetAllAdjustmentsQueryHandler,
)
from src.inventory.adjustment.infra.validators import (
    AddAdjustmentItemRequest,
    AdjustmentItemResponse,
    AdjustmentQueryParams,
    AdjustmentResponse,
    CreateAdjustmentRequest,
    UpdateAdjustmentItemRequest,
    UpdateAdjustmentRequest,
)


class AdjustmentRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "", response_model=list[AdjustmentResponse], summary="Get all adjustments"
        )(self.get_all)
        self.router.post(
            "", response_model=AdjustmentResponse, summary="Create adjustment"
        )(self.create)
        self.router.get(
            "/{id}", response_model=AdjustmentResponse, summary="Get adjustment by ID"
        )(self.get_by_id)
        self.router.put(
            "/{id}", response_model=AdjustmentResponse, summary="Update adjustment"
        )(self.update)
        self.router.delete("/{id}", status_code=204, summary="Delete adjustment")(
            self.delete
        )
        self.router.post(
            "/{id}/confirm",
            response_model=AdjustmentResponse,
            summary="Confirm adjustment",
        )(self.confirm)
        self.router.post(
            "/{id}/cancel",
            response_model=AdjustmentResponse,
            summary="Cancel adjustment",
        )(self.cancel)
        self.router.post(
            "/{id}/items",
            response_model=AdjustmentItemResponse,
            summary="Add item to adjustment",
        )(self.add_item)
        self.router.get(
            "/{id}/items",
            response_model=list[AdjustmentItemResponse],
            summary="Get adjustment items",
        )(self.get_items)

    def get_all(
        self,
        handler: Injected[GetAllAdjustmentsQueryHandler],
        query_params: AdjustmentQueryParams = Depends(),
    ) -> list[AdjustmentResponse]:
        """Get all inventory adjustments."""
        result = handler.handle(
            GetAllAdjustmentsQuery(**query_params.model_dump(exclude_none=True))
        )
        return [AdjustmentResponse.model_validate(a) for a in result]

    def create(
        self,
        body: CreateAdjustmentRequest,
        handler: Injected[CreateAdjustmentCommandHandler],
    ) -> AdjustmentResponse:
        """Create a new inventory adjustment in DRAFT status."""
        result = handler.handle(
            CreateAdjustmentCommand(
                **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return AdjustmentResponse.model_validate(result)

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetAdjustmentByIdQueryHandler],
    ) -> AdjustmentResponse:
        """Get an inventory adjustment by ID."""
        result = handler.handle(GetAdjustmentByIdQuery(id=id))
        return AdjustmentResponse.model_validate(result)

    def update(
        self,
        id: int,
        body: UpdateAdjustmentRequest,
        handler: Injected[UpdateAdjustmentCommandHandler],
    ) -> AdjustmentResponse:
        """Update an inventory adjustment (only DRAFT)."""
        result = handler.handle(
            UpdateAdjustmentCommand(
                id=id, **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return AdjustmentResponse.model_validate(result)

    def delete(
        self,
        id: int,
        handler: Injected[DeleteAdjustmentCommandHandler],
    ) -> None:
        """Delete an inventory adjustment (only DRAFT)."""
        handler.handle(DeleteAdjustmentCommand(id=id))

    def confirm(
        self,
        id: int,
        handler: Injected[ConfirmAdjustmentCommandHandler],
    ) -> AdjustmentResponse:
        """Confirm an inventory adjustment and generate stock movements."""
        result = handler.handle(ConfirmAdjustmentCommand(id=id))
        return AdjustmentResponse.model_validate(result)

    def cancel(
        self,
        id: int,
        handler: Injected[CancelAdjustmentCommandHandler],
    ) -> AdjustmentResponse:
        """Cancel an inventory adjustment (only DRAFT)."""
        result = handler.handle(CancelAdjustmentCommand(id=id))
        return AdjustmentResponse.model_validate(result)

    def add_item(
        self,
        id: int,
        body: AddAdjustmentItemRequest,
        handler: Injected[AddAdjustmentItemCommandHandler],
    ) -> AdjustmentItemResponse:
        """Add an item to an inventory adjustment."""
        result = handler.handle(
            AddAdjustmentItemCommand(
                adjustment_id=id,
                **body.model_dump(exclude_none=True, by_alias=False),
            )
        )
        return AdjustmentItemResponse.model_validate(result)

    def get_items(
        self,
        id: int,
        handler: Injected[GetAdjustmentItemsQueryHandler],
    ) -> list[AdjustmentItemResponse]:
        """Get all items for an inventory adjustment."""
        result = handler.handle(GetAdjustmentItemsQuery(adjustment_id=id))
        return [AdjustmentItemResponse.model_validate(item) for item in result]


class AdjustmentItemRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.put(
            "/{id}",
            response_model=AdjustmentItemResponse,
            summary="Update adjustment item",
        )(self.update)
        self.router.delete("/{id}", status_code=204, summary="Remove adjustment item")(
            self.remove
        )

    def update(
        self,
        id: int,
        body: UpdateAdjustmentItemRequest,
        handler: Injected[UpdateAdjustmentItemCommandHandler],
    ) -> AdjustmentItemResponse:
        """Update an adjustment item."""
        result = handler.handle(
            UpdateAdjustmentItemCommand(
                id=id, **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return AdjustmentItemResponse.model_validate(result)

    def remove(
        self,
        id: int,
        handler: Injected[RemoveAdjustmentItemCommandHandler],
    ) -> None:
        """Remove an item from an inventory adjustment."""
        handler.handle(RemoveAdjustmentItemCommand(id=id))
