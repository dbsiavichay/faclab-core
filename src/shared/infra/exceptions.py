from src.shared.domain.exceptions import BaseError


class NotFoundError(BaseError):
    def __init__(self, message: str):
        self.message = message
        self.status_code = 404
        super().__init__(self.status_code, self.message)
