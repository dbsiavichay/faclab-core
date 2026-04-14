from dataclasses import dataclass

from src.shared.domain.value_objects import ValueObject


@dataclass(frozen=True)
class PlainPassword(ValueObject):
    value: str

    def _validate(self):
        if not isinstance(self.value, str):
            raise ValueError("password must be a string")
        if len(self.value) < 8:
            raise ValueError("password must be at least 8 characters")
        if len(self.value) > 128:
            raise ValueError("password must be at most 128 characters")
