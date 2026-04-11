from fastapi import APIRouter, Depends
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
    PurchaseOrderQueryParams,
    PurchaseOrderRequest,
    PurchaseOrderResponse,
    PurchaseReceiptResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import (
    RESPONSES_COMMAND,
    RESPONSES_DELETE,
    RESPONSES_LIST,
    RESPONSES_QUERY,
    DataResponse,
    ListResponse,
    Meta,
    PaginatedDataResponse,
)


class PurchaseOrderRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[PurchaseOrderResponse],
            summary="Create purchase order",
            responses=RESPONSES_COMMAND,
        )(self.create)
        self.router.put(
            "/{id}",
            response_model=DataResponse[PurchaseOrderResponse],
            summary="Update purchase order",
            responses=RESPONSES_COMMAND,
        )(self.update)
        self.router.delete(
            "/{id}", summary="Delete purchase order", responses=RESPONSES_DELETE
        )(self.delete)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[PurchaseOrderResponse],
            summary="Get all purchase orders",
            responses=RESPONSES_LIST,
        )(self.get_all)
        self.router.get(
            "/{id}",
            response_model=DataResponse[PurchaseOrderResponse],
            summary="Get purchase order by ID",
            responses=RESPONSES_QUERY,
        )(self.get_by_id)
        self.router.post(
            "/{id}/send",
            response_model=DataResponse[PurchaseOrderResponse],
            summary="Send purchase order to supplier",
            responses=RESPONSES_COMMAND,
        )(self.send)
        self.router.post(
            "/{id}/cancel",
            response_model=DataResponse[PurchaseOrderResponse],
            summary="Cancel purchase order",
            responses=RESPONSES_COMMAND,
        )(self.cancel)
        self.router.post(
            "/{id}/receive",
            response_model=DataResponse[PurchaseReceiptResponse],
            summary="Receive goods for purchase order",
            responses=RESPONSES_COMMAND,
        )(self.receive)
        self.router.get(
            "/{id}/items",
            response_model=ListResponse[PurchaseOrderItemResponse],
            summary="Get items for a purchase order",
            responses=RESPONSES_LIST,
        )(self.get_items)
        self.router.get(
            "/{id}/receipts",
            response_model=ListResponse[PurchaseReceiptResponse],
            summary="Get receipts for a purchase order",
            responses=RESPONSES_LIST,
        )(self.get_receipts)

    def create(
        self,
        handler: Injected[CreatePurchaseOrderCommandHandler],
        body: PurchaseOrderRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderResponse]:
        """Creates a new purchase order."""
        result = handler.handle(
            CreatePurchaseOrderCommand(**body.model_dump(exclude_none=True))
        )
        return DataResponse(
            data=PurchaseOrderResponse.model_validate(result), meta=meta
        )

    def update(
        self,
        handler: Injected[UpdatePurchaseOrderCommandHandler],
        id: int,
        body: PurchaseOrderRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderResponse]:
        """Updates a purchase order (only DRAFT status)."""
        result = handler.handle(
            UpdatePurchaseOrderCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return DataResponse(
            data=PurchaseOrderResponse.model_validate(result), meta=meta
        )

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
        query_params: PurchaseOrderQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[PurchaseOrderResponse]:
        """Retrieves all purchase orders."""
        result = handler.handle(
            GetAllPurchaseOrdersQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[PurchaseOrderResponse.model_validate(po) for po in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )

    def get_by_id(
        self,
        handler: Injected[GetPurchaseOrderByIdQueryHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderResponse]:
        """Retrieves a purchase order by ID."""
        result = handler.handle(GetPurchaseOrderByIdQuery(id=id))
        return DataResponse(
            data=PurchaseOrderResponse.model_validate(result), meta=meta
        )

    def send(
        self,
        handler: Injected[SendPurchaseOrderCommandHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderResponse]:
        """Sends a purchase order to the supplier."""
        result = handler.handle(SendPurchaseOrderCommand(id=id))
        return DataResponse(
            data=PurchaseOrderResponse.model_validate(result), meta=meta
        )

    def cancel(
        self,
        handler: Injected[CancelPurchaseOrderCommandHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderResponse]:
        """Cancels a purchase order."""
        result = handler.handle(CancelPurchaseOrderCommand(id=id))
        return DataResponse(
            data=PurchaseOrderResponse.model_validate(result), meta=meta
        )

    def receive(
        self,
        handler: Injected[CreatePurchaseReceiptCommandHandler],
        id: int,
        body: CreatePurchaseReceiptRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseReceiptResponse]:
        """Registers a goods receipt for a purchase order."""
        items = [
            ReceiveItemInput(
                purchase_order_item_id=item.purchase_order_item_id,
                quantity_received=item.quantity_received,
                location_id=item.location_id,
                lot_number=item.lot_number,
                serial_numbers=item.serial_numbers,
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
        return DataResponse(
            data=PurchaseReceiptResponse.model_validate(result), meta=meta
        )

    def get_items(
        self,
        handler: Injected[GetPurchaseOrderItemsByPOQueryHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[PurchaseOrderItemResponse]:
        """Retrieves all items for a purchase order."""
        result = handler.handle(GetPurchaseOrderItemsByPOQuery(purchase_order_id=id))
        return ListResponse(
            data=[PurchaseOrderItemResponse.model_validate(item) for item in result],
            meta=meta,
        )

    def get_receipts(
        self,
        handler: Injected[GetReceiptsByPurchaseOrderQueryHandler],
        id: int,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[PurchaseReceiptResponse]:
        """Retrieves all receipts for a purchase order."""
        result = handler.handle(GetReceiptsByPurchaseOrderQuery(purchase_order_id=id))
        return ListResponse(
            data=[PurchaseReceiptResponse.model_validate(r) for r in result],
            meta=meta,
        )


class POItemRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[PurchaseOrderItemResponse],
            summary="Add item to purchase order",
            responses=RESPONSES_COMMAND,
        )(self.add)
        self.router.put(
            "/{id}",
            response_model=DataResponse[PurchaseOrderItemResponse],
            summary="Update purchase order item",
            responses=RESPONSES_COMMAND,
        )(self.update)
        self.router.delete(
            "/{id}", summary="Remove purchase order item", responses=RESPONSES_DELETE
        )(self.remove)

    def add(
        self,
        handler: Injected[AddPurchaseOrderItemCommandHandler],
        body: PurchaseOrderItemRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderItemResponse]:
        """Adds an item to a purchase order."""
        result = handler.handle(
            AddPurchaseOrderItemCommand(**body.model_dump(exclude_none=True))
        )
        return DataResponse(
            data=PurchaseOrderItemResponse.model_validate(result), meta=meta
        )

    def update(
        self,
        handler: Injected[UpdatePurchaseOrderItemCommandHandler],
        id: int,
        body: PurchaseOrderItemUpdateRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PurchaseOrderItemResponse]:
        """Updates a purchase order item."""
        result = handler.handle(
            UpdatePurchaseOrderItemCommand(id=id, **body.model_dump(exclude_none=True))
        )
        return DataResponse(
            data=PurchaseOrderItemResponse.model_validate(result), meta=meta
        )

    def remove(
        self,
        handler: Injected[RemovePurchaseOrderItemCommandHandler],
        id: int,
    ) -> None:
        """Removes an item from a purchase order."""
        handler.handle(RemovePurchaseOrderItemCommand(id=id))
