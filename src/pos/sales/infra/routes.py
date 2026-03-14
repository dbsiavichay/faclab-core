"""POS sale routes"""

from fastapi import APIRouter, Depends, status
from wireup import Injected

from src.pos.sales.app.commands.apply_discount import (
    ApplySaleDiscountCommand,
    ApplySaleDiscountCommandHandler,
)
from src.pos.sales.app.commands.cancel_sale import (
    POSCancelSaleCommand,
    POSCancelSaleCommandHandler,
)
from src.pos.sales.app.commands.confirm_sale import (
    POSConfirmSaleCommand,
    POSConfirmSaleCommandHandler,
)
from src.pos.sales.app.commands.create_sale import (
    POSCreateSaleCommand,
    POSCreateSaleCommandHandler,
)
from src.pos.sales.app.commands.park_sale import (
    ParkSaleCommand,
    POSParkSaleCommandHandler,
)
from src.pos.sales.app.commands.resume_sale import (
    POSResumeSaleCommandHandler,
    ResumeSaleCommand,
)
from src.pos.sales.app.queries.get_parked_sales import (
    GetParkedSalesQuery,
    GetParkedSalesQueryHandler,
)
from src.pos.sales.infra.validators import (
    ApplyDiscountRequest,
    ParkSaleRequest,
    POSSaleRequest,
)
from src.sales.app.commands.add_sale_item import (
    AddSaleItemCommand,
    AddSaleItemCommandHandler,
)
from src.sales.app.commands.register_payment import (
    RegisterPaymentCommand,
    RegisterPaymentCommandHandler,
)
from src.sales.app.commands.remove_sale_item import (
    RemoveSaleItemCommand,
    RemoveSaleItemCommandHandler,
)
from src.sales.app.commands.update_sale_item import (
    UpdateSaleItemCommand,
    UpdateSaleItemCommandHandler,
)
from src.sales.app.queries.get_payments import (
    GetSalePaymentsQuery,
    GetSalePaymentsQueryHandler,
)
from src.sales.app.queries.get_sale_items import (
    GetSaleItemsQuery,
    GetSaleItemsQueryHandler,
)
from src.sales.app.queries.get_sales import GetSaleByIdQuery, GetSaleByIdQueryHandler
from src.sales.infra.validators import (
    CancelSaleRequest,
    PaymentRequest,
    PaymentResponse,
    SaleItemRequest,
    SaleItemResponse,
    SaleItemUpdateRequest,
    SaleResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, ListResponse, Meta


class POSSaleRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[SaleResponse],
            status_code=status.HTTP_201_CREATED,
            summary="Create sale",
        )(self.create_sale)
        self.router.get(
            "/parked",
            response_model=ListResponse[SaleResponse],
            summary="List parked sales",
        )(self.get_parked_sales)
        self.router.get(
            "/{sale_id}",
            response_model=DataResponse[SaleResponse],
            summary="Get sale",
        )(self.get_sale)
        self.router.post(
            "/{sale_id}/items",
            response_model=DataResponse[SaleItemResponse],
            status_code=status.HTTP_201_CREATED,
            summary="Add item to sale",
        )(self.add_sale_item)
        self.router.get(
            "/{sale_id}/items",
            response_model=ListResponse[SaleItemResponse],
            summary="List sale items",
        )(self.get_sale_items)
        self.router.put(
            "/{sale_id}/items/{item_id}",
            response_model=DataResponse[SaleItemResponse],
            summary="Update sale item",
        )(self.update_sale_item)
        self.router.delete(
            "/{sale_id}/items/{item_id}", summary="Remove item from sale"
        )(self.remove_sale_item)
        self.router.post(
            "/{sale_id}/confirm",
            response_model=DataResponse[SaleResponse],
            summary="Confirm sale",
        )(self.confirm_sale)
        self.router.post(
            "/{sale_id}/cancel",
            response_model=DataResponse[SaleResponse],
            summary="Cancel sale",
        )(self.cancel_sale)
        self.router.post(
            "/{sale_id}/park",
            response_model=DataResponse[SaleResponse],
            summary="Park sale",
        )(self.park_sale)
        self.router.post(
            "/{sale_id}/resume",
            response_model=DataResponse[SaleResponse],
            summary="Resume parked sale",
        )(self.resume_sale)
        self.router.post(
            "/{sale_id}/discount",
            response_model=DataResponse[SaleResponse],
            summary="Apply discount to sale",
        )(self.apply_discount)
        self.router.post(
            "/{sale_id}/payments",
            response_model=DataResponse[PaymentResponse],
            status_code=status.HTTP_201_CREATED,
            summary="Register payment",
        )(self.register_payment)
        self.router.get(
            "/{sale_id}/payments",
            response_model=ListResponse[PaymentResponse],
            summary="List sale payments",
        )(self.get_sale_payments)

    def create_sale(
        self,
        handler: Injected[POSCreateSaleCommandHandler],
        sale: POSSaleRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        result = handler.handle(
            POSCreateSaleCommand(**sale.model_dump(exclude_none=True))
        )
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def get_sale(
        self,
        handler: Injected[GetSaleByIdQueryHandler],
        sale_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        result = handler.handle(GetSaleByIdQuery(sale_id=sale_id))
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def add_sale_item(
        self,
        handler: Injected[AddSaleItemCommandHandler],
        sale_id: int,
        item: SaleItemRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleItemResponse]:
        result = handler.handle(
            AddSaleItemCommand(sale_id=sale_id, **item.model_dump(exclude_none=True))
        )
        return DataResponse(data=SaleItemResponse.model_validate(result), meta=meta)

    def get_sale_items(
        self,
        handler: Injected[GetSaleItemsQueryHandler],
        sale_id: int,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[SaleItemResponse]:
        result = handler.handle(GetSaleItemsQuery(sale_id=sale_id))
        return ListResponse(
            data=[SaleItemResponse.model_validate(r) for r in result], meta=meta
        )

    def update_sale_item(
        self,
        handler: Injected[UpdateSaleItemCommandHandler],
        sale_id: int,
        item_id: int,
        item: SaleItemUpdateRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleItemResponse]:
        result = handler.handle(
            UpdateSaleItemCommand(
                sale_id=sale_id,
                sale_item_id=item_id,
                **item.model_dump(exclude_none=True),
            )
        )
        return DataResponse(data=SaleItemResponse.model_validate(result), meta=meta)

    def remove_sale_item(
        self,
        handler: Injected[RemoveSaleItemCommandHandler],
        sale_id: int,
        item_id: int,
    ) -> dict:
        return handler.handle(
            RemoveSaleItemCommand(sale_id=sale_id, sale_item_id=item_id)
        )

    def confirm_sale(
        self,
        handler: Injected[POSConfirmSaleCommandHandler],
        sale_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        result = handler.handle(POSConfirmSaleCommand(sale_id=sale_id))
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def cancel_sale(
        self,
        handler: Injected[POSCancelSaleCommandHandler],
        sale_id: int,
        cancel_input: CancelSaleRequest | None = None,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        reason = cancel_input.reason if cancel_input else None
        result = handler.handle(POSCancelSaleCommand(sale_id=sale_id, reason=reason))
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def apply_discount(
        self,
        handler: Injected[ApplySaleDiscountCommandHandler],
        sale_id: int,
        discount_input: ApplyDiscountRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        result = handler.handle(
            ApplySaleDiscountCommand(sale_id=sale_id, **discount_input.model_dump())
        )
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def register_payment(
        self,
        handler: Injected[RegisterPaymentCommandHandler],
        sale_id: int,
        payment: PaymentRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[PaymentResponse]:
        result = handler.handle(
            RegisterPaymentCommand(
                sale_id=sale_id, **payment.model_dump(exclude_none=True)
            )
        )
        return DataResponse(data=PaymentResponse.model_validate(result), meta=meta)

    def get_sale_payments(
        self,
        handler: Injected[GetSalePaymentsQueryHandler],
        sale_id: int,
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[PaymentResponse]:
        result = handler.handle(GetSalePaymentsQuery(sale_id=sale_id))
        return ListResponse(
            data=[PaymentResponse.model_validate(r) for r in result], meta=meta
        )

    def park_sale(
        self,
        handler: Injected[POSParkSaleCommandHandler],
        sale_id: int,
        park_input: ParkSaleRequest | None = None,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        reason = park_input.reason if park_input else None
        result = handler.handle(ParkSaleCommand(sale_id=sale_id, reason=reason))
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def resume_sale(
        self,
        handler: Injected[POSResumeSaleCommandHandler],
        sale_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[SaleResponse]:
        result = handler.handle(ResumeSaleCommand(sale_id=sale_id))
        return DataResponse(data=SaleResponse.model_validate(result), meta=meta)

    def get_parked_sales(
        self,
        handler: Injected[GetParkedSalesQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> ListResponse[SaleResponse]:
        result = handler.handle(GetParkedSalesQuery())
        return ListResponse(
            data=[SaleResponse.model_validate(r) for r in result], meta=meta
        )
