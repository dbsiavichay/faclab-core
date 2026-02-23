from fastapi import APIRouter, Depends
from wireup import Injected

from src.inventory.transfer.app.commands.transfer import (
    AddTransferItemCommand,
    AddTransferItemCommandHandler,
    CancelStockTransferCommand,
    CancelStockTransferCommandHandler,
    ConfirmStockTransferCommand,
    ConfirmStockTransferCommandHandler,
    CreateStockTransferCommand,
    CreateStockTransferCommandHandler,
    DeleteStockTransferCommand,
    DeleteStockTransferCommandHandler,
    ReceiveStockTransferCommand,
    ReceiveStockTransferCommandHandler,
    RemoveTransferItemCommand,
    RemoveTransferItemCommandHandler,
    UpdateStockTransferCommand,
    UpdateStockTransferCommandHandler,
    UpdateTransferItemCommand,
    UpdateTransferItemCommandHandler,
)
from src.inventory.transfer.app.queries.transfer import (
    GetAllTransfersQuery,
    GetAllTransfersQueryHandler,
    GetTransferByIdQuery,
    GetTransferByIdQueryHandler,
    GetTransferItemsQuery,
    GetTransferItemsQueryHandler,
)
from src.inventory.transfer.infra.validators import (
    AddTransferItemRequest,
    CreateTransferRequest,
    TransferItemResponse,
    TransferQueryParams,
    TransferResponse,
    UpdateTransferItemRequest,
    UpdateTransferRequest,
)


class TransferRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get(
            "", response_model=list[TransferResponse], summary="Get all transfers"
        )(self.get_all)
        self.router.post(
            "", response_model=TransferResponse, summary="Create transfer"
        )(self.create)
        self.router.get(
            "/{id}", response_model=TransferResponse, summary="Get transfer by ID"
        )(self.get_by_id)
        self.router.put(
            "/{id}", response_model=TransferResponse, summary="Update transfer"
        )(self.update)
        self.router.delete("/{id}", status_code=204, summary="Delete transfer")(
            self.delete
        )
        self.router.post(
            "/{id}/confirm",
            response_model=TransferResponse,
            summary="Confirm transfer",
        )(self.confirm)
        self.router.post(
            "/{id}/receive",
            response_model=TransferResponse,
            summary="Receive transfer",
        )(self.receive)
        self.router.post(
            "/{id}/cancel",
            response_model=TransferResponse,
            summary="Cancel transfer",
        )(self.cancel)
        self.router.post(
            "/{id}/items",
            response_model=TransferItemResponse,
            summary="Add item to transfer",
        )(self.add_item)
        self.router.get(
            "/{id}/items",
            response_model=list[TransferItemResponse],
            summary="Get transfer items",
        )(self.get_items)

    def get_all(
        self,
        handler: Injected[GetAllTransfersQueryHandler],
        query_params: TransferQueryParams = Depends(),
    ) -> list[TransferResponse]:
        """Get all stock transfers."""
        result = handler.handle(
            GetAllTransfersQuery(**query_params.model_dump(exclude_none=True))
        )
        return [TransferResponse.model_validate(t) for t in result]

    def create(
        self,
        body: CreateTransferRequest,
        handler: Injected[CreateStockTransferCommandHandler],
    ) -> TransferResponse:
        """Create a new stock transfer in DRAFT status."""
        result = handler.handle(
            CreateStockTransferCommand(
                **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return TransferResponse.model_validate(result)

    def get_by_id(
        self,
        id: int,
        handler: Injected[GetTransferByIdQueryHandler],
    ) -> TransferResponse:
        """Get a stock transfer by ID."""
        result = handler.handle(GetTransferByIdQuery(id=id))
        return TransferResponse.model_validate(result)

    def update(
        self,
        id: int,
        body: UpdateTransferRequest,
        handler: Injected[UpdateStockTransferCommandHandler],
    ) -> TransferResponse:
        """Update a stock transfer (only DRAFT)."""
        result = handler.handle(
            UpdateStockTransferCommand(
                id=id, **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return TransferResponse.model_validate(result)

    def delete(
        self,
        id: int,
        handler: Injected[DeleteStockTransferCommandHandler],
    ) -> None:
        """Delete a stock transfer (only DRAFT)."""
        handler.handle(DeleteStockTransferCommand(id=id))

    def confirm(
        self,
        id: int,
        handler: Injected[ConfirmStockTransferCommandHandler],
    ) -> TransferResponse:
        """Confirm a stock transfer — reserves stock at source location."""
        result = handler.handle(ConfirmStockTransferCommand(id=id))
        return TransferResponse.model_validate(result)

    def receive(
        self,
        id: int,
        handler: Injected[ReceiveStockTransferCommandHandler],
    ) -> TransferResponse:
        """Receive a stock transfer — creates OUT/IN movements and moves stock."""
        result = handler.handle(ReceiveStockTransferCommand(id=id))
        return TransferResponse.model_validate(result)

    def cancel(
        self,
        id: int,
        handler: Injected[CancelStockTransferCommandHandler],
    ) -> TransferResponse:
        """Cancel a stock transfer — releases reservations if CONFIRMED."""
        result = handler.handle(CancelStockTransferCommand(id=id))
        return TransferResponse.model_validate(result)

    def add_item(
        self,
        id: int,
        body: AddTransferItemRequest,
        handler: Injected[AddTransferItemCommandHandler],
    ) -> TransferItemResponse:
        """Add an item to a stock transfer."""
        result = handler.handle(
            AddTransferItemCommand(
                transfer_id=id,
                **body.model_dump(exclude_none=True, by_alias=False),
            )
        )
        return TransferItemResponse.model_validate(result)

    def get_items(
        self,
        id: int,
        handler: Injected[GetTransferItemsQueryHandler],
    ) -> list[TransferItemResponse]:
        """Get all items for a stock transfer."""
        result = handler.handle(GetTransferItemsQuery(transfer_id=id))
        return [TransferItemResponse.model_validate(item) for item in result]


class TransferItemRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.put(
            "/{id}",
            response_model=TransferItemResponse,
            summary="Update transfer item",
        )(self.update)
        self.router.delete("/{id}", status_code=204, summary="Remove transfer item")(
            self.remove
        )

    def update(
        self,
        id: int,
        body: UpdateTransferItemRequest,
        handler: Injected[UpdateTransferItemCommandHandler],
    ) -> TransferItemResponse:
        """Update a transfer item."""
        result = handler.handle(
            UpdateTransferItemCommand(
                id=id, **body.model_dump(exclude_none=True, by_alias=False)
            )
        )
        return TransferItemResponse.model_validate(result)

    def remove(
        self,
        id: int,
        handler: Injected[RemoveTransferItemCommandHandler],
    ) -> None:
        """Remove an item from a stock transfer."""
        handler.handle(RemoveTransferItemCommand(id=id))
