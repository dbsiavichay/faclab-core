from src.shared.domain.exceptions import DomainError


class CashMovementError(DomainError):
    error_code = "CASH_MOVEMENT_ERROR"


class InvalidCashMovementAmountError(CashMovementError):
    error_code = "INVALID_CASH_MOVEMENT_AMOUNT"

    def __init__(self):
        super().__init__(
            message="Cash movement amount must be greater than zero",
            detail="amount must be > 0",
        )


class ShiftNotOpenForCashMovementError(CashMovementError):
    error_code = "SHIFT_NOT_OPEN_FOR_CASH_MOVEMENT"

    def __init__(self, shift_id: int):
        super().__init__(
            message=f"Shift {shift_id} is not open for cash movements",
            detail=f"shift_id={shift_id}",
        )
