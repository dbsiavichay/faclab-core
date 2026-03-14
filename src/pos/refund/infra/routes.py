from fastapi import APIRouter, Depends, status
from wireup import Injected

from src.pos.refund.app.commands.cancel_refund import (
    CancelRefundCommand,
    CancelRefundCommandHandler,
)
from src.pos.refund.app.commands.create_refund import (
    CreateRefundCommand,
    CreateRefundCommandHandler,
)
from src.pos.refund.app.commands.process_refund import (
    ProcessRefundCommand,
    ProcessRefundCommandHandler,
)
from src.pos.refund.app.queries.get_refunds import (
    GetRefundByIdQuery,
    GetRefundByIdQueryHandler,
    GetRefundsQuery,
    GetRefundsQueryHandler,
)
from src.pos.refund.infra.validators import (
    CreateRefundRequest,
    ProcessRefundRequest,
    RefundDetailResponse,
    RefundQueryParams,
    RefundResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, Meta, PaginatedDataResponse


class POSRefundRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "",
            response_model=DataResponse[RefundDetailResponse],
            status_code=status.HTTP_201_CREATED,
            summary="Create refund",
        )(self.create_refund)
        self.router.post(
            "/{refund_id}/process",
            response_model=DataResponse[RefundDetailResponse],
            summary="Process refund",
        )(self.process_refund)
        self.router.post(
            "/{refund_id}/cancel",
            response_model=DataResponse[RefundResponse],
            summary="Cancel refund",
        )(self.cancel_refund)
        self.router.get(
            "/{refund_id}",
            response_model=DataResponse[RefundDetailResponse],
            summary="Get refund",
        )(self.get_refund)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[RefundResponse],
            summary="List refunds",
        )(self.list_refunds)

    def create_refund(
        self,
        handler: Injected[CreateRefundCommandHandler],
        refund_input: CreateRefundRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[RefundDetailResponse]:
        result = handler.handle(
            CreateRefundCommand(
                original_sale_id=refund_input.original_sale_id,
                items=[item.model_dump() for item in refund_input.items],
                reason=refund_input.reason,
                refunded_by=refund_input.refunded_by,
            )
        )
        return DataResponse(data=RefundDetailResponse.model_validate(result), meta=meta)

    def process_refund(
        self,
        handler: Injected[ProcessRefundCommandHandler],
        refund_id: int,
        process_input: ProcessRefundRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[RefundDetailResponse]:
        result = handler.handle(
            ProcessRefundCommand(
                refund_id=refund_id,
                payments=[p.model_dump() for p in process_input.payments],
            )
        )
        return DataResponse(data=RefundDetailResponse.model_validate(result), meta=meta)

    def cancel_refund(
        self,
        handler: Injected[CancelRefundCommandHandler],
        refund_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[RefundResponse]:
        result = handler.handle(CancelRefundCommand(refund_id=refund_id))
        return DataResponse(data=RefundResponse.model_validate(result), meta=meta)

    def get_refund(
        self,
        handler: Injected[GetRefundByIdQueryHandler],
        refund_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[RefundDetailResponse]:
        result = handler.handle(GetRefundByIdQuery(refund_id=refund_id))
        return DataResponse(data=RefundDetailResponse.model_validate(result), meta=meta)

    def list_refunds(
        self,
        handler: Injected[GetRefundsQueryHandler],
        meta: Meta = Depends(get_meta),
        params: RefundQueryParams = Depends(),
    ) -> PaginatedDataResponse[RefundResponse]:
        result = handler.handle(
            GetRefundsQuery(
                sale_id=params.sale_id,
                status=params.status,
                limit=params.limit,
                offset=params.offset,
            )
        )
        return PaginatedDataResponse(
            data=[RefundResponse.model_validate(r) for r in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=params.limit,
                offset=params.offset,
            ),
        )
