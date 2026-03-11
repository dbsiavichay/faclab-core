"""POS routes for Shifts"""

from fastapi import APIRouter, Depends, status
from wireup import Injected

from src.pos.shift.app.commands.close_shift import (
    CloseShiftCommand,
    CloseShiftCommandHandler,
)
from src.pos.shift.app.commands.open_shift import (
    OpenShiftCommand,
    OpenShiftCommandHandler,
)
from src.pos.shift.app.queries.get_shifts import (
    GetActiveShiftQuery,
    GetActiveShiftQueryHandler,
    GetAllShiftsQuery,
    GetAllShiftsQueryHandler,
    GetShiftByIdQuery,
    GetShiftByIdQueryHandler,
)
from src.pos.shift.infra.validators import (
    CloseShiftRequest,
    OpenShiftRequest,
    ShiftQueryParams,
    ShiftResponse,
)
from src.shared.infra.dependencies import get_meta
from src.shared.infra.validators import DataResponse, Meta, PaginatedDataResponse


class POSShiftRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.post(
            "/open",
            response_model=DataResponse[ShiftResponse],
            status_code=status.HTTP_201_CREATED,
            summary="Open shift",
        )(self.open_shift)
        self.router.post(
            "/{shift_id}/close",
            response_model=DataResponse[ShiftResponse],
            summary="Close shift",
        )(self.close_shift)
        self.router.get(
            "/active",
            response_model=DataResponse[ShiftResponse | None],
            summary="Get active shift",
        )(self.get_active_shift)
        self.router.get(
            "/{shift_id}",
            response_model=DataResponse[ShiftResponse],
            summary="Get shift by ID",
        )(self.get_shift)
        self.router.get(
            "",
            response_model=PaginatedDataResponse[ShiftResponse],
            summary="List all shifts",
        )(self.get_all_shifts)

    def open_shift(
        self,
        handler: Injected[OpenShiftCommandHandler],
        data: OpenShiftRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ShiftResponse]:
        result = handler.handle(
            OpenShiftCommand(
                cashier_name=data.cashier_name,
                opening_balance=data.opening_balance,
                notes=data.notes,
            )
        )
        return DataResponse(data=ShiftResponse.model_validate(result), meta=meta)

    def close_shift(
        self,
        handler: Injected[CloseShiftCommandHandler],
        shift_id: int,
        data: CloseShiftRequest,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ShiftResponse]:
        result = handler.handle(
            CloseShiftCommand(
                shift_id=shift_id,
                closing_balance=data.closing_balance,
                notes=data.notes,
            )
        )
        return DataResponse(data=ShiftResponse.model_validate(result), meta=meta)

    def get_active_shift(
        self,
        handler: Injected[GetActiveShiftQueryHandler],
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ShiftResponse | None]:
        result = handler.handle(GetActiveShiftQuery())
        data = ShiftResponse.model_validate(result) if result is not None else None
        return DataResponse(data=data, meta=meta)

    def get_shift(
        self,
        handler: Injected[GetShiftByIdQueryHandler],
        shift_id: int,
        meta: Meta = Depends(get_meta),
    ) -> DataResponse[ShiftResponse]:
        result = handler.handle(GetShiftByIdQuery(shift_id=shift_id))
        return DataResponse(data=ShiftResponse.model_validate(result), meta=meta)

    def get_all_shifts(
        self,
        handler: Injected[GetAllShiftsQueryHandler],
        query_params: ShiftQueryParams = Depends(),
        meta: Meta = Depends(get_meta),
    ) -> PaginatedDataResponse[ShiftResponse]:
        result = handler.handle(
            GetAllShiftsQuery(**query_params.model_dump(exclude_none=True))
        )
        return PaginatedDataResponse(
            data=[ShiftResponse.model_validate(r) for r in result["items"]],
            meta=meta.with_pagination(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
            ),
        )
