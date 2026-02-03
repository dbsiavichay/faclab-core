from src.shared.domain.exceptions import BaseException


class InvalidMovementTypeException(BaseException):
    def __init__(self, detail: str):
        self.code = 400
        self.message = "El tipo de movimiento no es válido"
        self.detail = detail
        super().__init__(self.code, self.message, detail)
