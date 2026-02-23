from fastapi import APIRouter, Query
from wireup import Injected

from src.purchasing.app.commands.purchase_order import (
    CancelPurchaseOrderCommand,
    CancelPurchaseOrderCommandHandler,
    CreatePurchaseOrderCommand,
    CreatePurchaseOrderCommandHandler,
    DeletePurchaseOrderCommand,
    DeletePurchaseOrderCommandHandler,
    SendPurchaseOrderCommand,
    SendPurchaseOrderCommandHandler,
    UpdatePurchaseOrderCommand,
    UpdatePurchaseOrderCommandHandler,
)
from src.purchasing.app.commands.purchase_order_item import (
    AddPurchaseOrderItemCommand,
    AddPurchaseOrderItemCommandHandler,
    RemovePurchaseOrderItemCommand,
    RemovePurchaseOrderItemCommandHandler,
    UpdatePurchaseOrderItemCommand,
    UpdatePurchaseOrderItemCommandHandler,
)
from src.purchasing.app.commands.purchase_receipt import (
    CreatePurchaseReceiptCommand,
    CreatePurchaseReceiptCommandHandler,
    ReceiveItemInput,
)
from src.purchasing.app.queries.purchase_order import (
    GetAllPurchaseOrdersQuery,
    GetAllPurchaseOrdersQueryHandler,
    GetPurchaseOrderByIdQuery,
    GetPurchaseOrderByIdQueryHandler,
)
from src.purchasing.app.queries.purchase_order_item import (
    GetPurchaseOrderItemsByPOQuery,
    GetPurchaseOrderItemsByPOQueryHandler,
)
from src.purchasing.app.queries.purchase_receipt import (
    GetReceiptsByPurchaseOrderQuery,
    GetReceiptsByPurchaseOrderQueryHandler,
)
from src.purchasing.infra.validators import (
    CreatePurchaseReceiptRequest,
    PurchaseOrderItemRequest,
    PurchaseOrderItemResponse,
    PurchaseOrderItemUpdateRequest,
    PurchaseOrderRequest,
    PurchaseOrderResponse,
    PurchaseReceiptResponse,
)


class PurchaseOrderRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=PurchaseOrderResponse,
            summary="Create purchase order",
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=PurchaseOrderResponse,
            summary="Update purchase order",
        )(self.update)
        self.router.delete("/{id}", summary="Delete purchase order")(self.delete)
        self.router.get(
            "",
            response_model=list[PurchaseOrderResponse],
            summary="Get all purchase orders",
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=PurchaseOrderResponse,
            summary="Get purchase order by ID",
        )(self.get_by_id)
        self.router.post(
            "/{id}/send",
            response_model=PurchaseOrderResponse,
            summary="Send purchase order to supplier",
        )(self.send)
        self.router.post(
            "/{id}/cancel",
            response_model=PurchaseOrderResponse,
            summary="Cancel purchase order",
        )(self.cancel)
        self.router.post(
            "/{id}/receive",
            response_model=PurchaseReceiptResponse,
            summary="Receive goods for purchase order",
        )(self.receive)
        self.router.get(
            "/{id}/items",
            response_model=list[PurchaseOrderItemResponse],
            summary="Get items for a purchase order",
        )(self.get_items)
        self.router.get(
            "/{id}/receipts",
            response_model=list[PurchaseReceiptResponse],
            summary="Get receipts for a purchase order",
        )(self.get_receipts)

    def create(
        self,
        handler: Injected[CreatePurchaseOrderCommandHandler],
        body: PurchaseOrderRequest,
    ) -> PurchaseOrderResponse:
        """Creates a new purchase order."""
        result = handler.handle(
            CreatePurchaseOrderCommand(**body.model_dump(exclude_none=True))
        )
        return PurchaseOrderResponse.model_validate(result)

    def update(
        self,
        handler: Injected[UpdatePurchaseOrderCommandHandler],
        id: int,
        body: PurchaseOrderRequest,
    ) -> PurchaseOrderResponse:
        """Updates a purchase order (only DRAFT status)."""
        result = handler.handle(
            UpdatePurchaseOrderCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return PurchaseOrderResponse.model_validate(result)

    def delete(
        self,
        handler: Injected[DeletePurchaseOrderCommandHandler],
        id: int,
    ) -> None:
        """Deletes a purchase order (only DRAFT status)."""
        handler.handle(DeletePurchaseOrderCommand(id=id))

    def get_all(
        self,
        handler: Injected[GetAllPurchaseOrdersQueryHandler],
        status: str | None = Query(None, description="Filter by status"),
        supplier_id: int | None = Query(None, description="Filter by supplier ID"),
    ) -> list[PurchaseOrderResponse]:
        """Retrieves all purchase orders."""
        result = handler.handle(
            GetAllPurchaseOrdersQuery(status=status, supplier_id=supplier_id)
        )
        return [PurchaseOrderResponse.model_validate(po) for po in result]

    def get_by_id(
        self,
        handler: Injected[GetPurchaseOrderByIdQueryHandler],
        id: int,
    ) -> PurchaseOrderResponse:
        """Retrieves a purchase order by ID."""
        result = handler.handle(GetPurchaseOrderByIdQuery(id=id))
        return PurchaseOrderResponse.model_validate(result)

    def send(
        self,
        handler: Injected[SendPurchaseOrderCommandHandler],
        id: int,
    ) -> PurchaseOrderResponse:
        """Sends a purchase order to the supplier."""
        result = handler.handle(SendPurchaseOrderCommand(id=id))
        return PurchaseOrderResponse.model_validate(result)

    def cancel(
        self,
        handler: Injected[CancelPurchaseOrderCommandHandler],
        id: int,
    ) -> PurchaseOrderResponse:
        """Cancels a purchase order."""
        result = handler.handle(CancelPurchaseOrderCommand(id=id))
        return PurchaseOrderResponse.model_validate(result)

    def receive(
        self,
        handler: Injected[CreatePurchaseReceiptCommandHandler],
        id: int,
        body: CreatePurchaseReceiptRequest,
    ) -> PurchaseReceiptResponse:
        """Registers a goods receipt for a purchase order."""
        items = [
            ReceiveItemInput(
                purchase_order_item_id=item.purchase_order_item_id,
                quantity_received=item.quantity_received,
                location_id=item.location_id,
            )
            for item in body.items
        ]
        result = handler.handle(
            CreatePurchaseReceiptCommand(
                purchase_order_id=id,
                items=items,
                notes=body.notes,
                received_at=body.received_at,
            )
        )
        return PurchaseReceiptResponse.model_validate(result)

    def get_items(
        self,
        handler: Injected[GetPurchaseOrderItemsByPOQueryHandler],
        id: int,
    ) -> list[PurchaseOrderItemResponse]:
        """Retrieves all items for a purchase order."""
        result = handler.handle(GetPurchaseOrderItemsByPOQuery(purchase_order_id=id))
        return [PurchaseOrderItemResponse.model_validate(item) for item in result]

    def get_receipts(
        self,
        handler: Injected[GetReceiptsByPurchaseOrderQueryHandler],
        id: int,
    ) -> list[PurchaseReceiptResponse]:
        """Retrieves all receipts for a purchase order."""
        result = handler.handle(GetReceiptsByPurchaseOrderQuery(purchase_order_id=id))
        return [PurchaseReceiptResponse.model_validate(r) for r in result]


class POItemRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=PurchaseOrderItemResponse,
            summary="Add item to purchase order",
        )(self.add)
        self.router.put(
            "/{id}",
            response_model=PurchaseOrderItemResponse,
            summary="Update purchase order item",
        )(self.update)
        self.router.delete("/{id}", summary="Remove purchase order item")(self.remove)

    def add(
        self,
        handler: Injected[AddPurchaseOrderItemCommandHandler],
        body: PurchaseOrderItemRequest,
    ) -> PurchaseOrderItemResponse:
        """Adds an item to a purchase order."""
        result = handler.handle(
            AddPurchaseOrderItemCommand(**body.model_dump(exclude_none=True))
        )
        return PurchaseOrderItemResponse.model_validate(result)

    def update(
        self,
        handler: Injected[UpdatePurchaseOrderItemCommandHandler],
        id: int,
        body: PurchaseOrderItemUpdateRequest,
    ) -> PurchaseOrderItemResponse:
        """Updates a purchase order item."""
        result = handler.handle(
            UpdatePurchaseOrderItemCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return PurchaseOrderItemResponse.model_validate(result)

    def remove(
        self,
        handler: Injected[RemovePurchaseOrderItemCommandHandler],
        id: int,
    ) -> None:
        """Removes an item from a purchase order."""
        handler.handle(RemovePurchaseOrderItemCommand(id=id))
