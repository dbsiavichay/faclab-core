from src.shared.domain.exceptions import DomainError


class InvalidMovementTypeError(DomainError):
    error_code = "INVALID_MOVEMENT_TYPE"

    def __init__(self, detail: str):
        super().__init__(
            message="El tipo de movimiento no es válido",
            detail=detail,
        )
