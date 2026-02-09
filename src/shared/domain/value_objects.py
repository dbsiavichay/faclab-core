import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ValueObject(ABC):
    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self):
        raise NotImplementedError


@dataclass(frozen=True)
class Money(ValueObject):
    amount: Decimal
    currency: str = "USD"

    def _validate(self):
        if not isinstance(self.amount, Decimal):
            raise ValueError("amount must be a Decimal")
        if self.amount < 0:
            raise ValueError("amount cannot be negative")
        if not self.currency:
            raise ValueError("currency is required")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Result cannot be negative")
        return Money(amount=result, currency=self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError(f"Cannot multiply Money by {type(factor)}")
        result = self.amount * Decimal(str(factor))
        return Money(amount=result, currency=self.currency)


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def _validate(self):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email: {self.value}")


@dataclass(frozen=True)
class TaxId(ValueObject):
    value: str
    country: str = "EC"

    def _validate(self):
        if self.country == "EC":
            if not re.match(r"^\d{13}$", self.value):
                raise ValueError(
                    f"Invalid Ecuadorian RUC: {self.value}. Must be 13 digits."
                )
        else:
            if not self.value:
                raise ValueError("TaxId value is required")

    def formatted(self) -> str:
        if self.country == "EC":
            return f"{self.value[:4]}-{self.value[4:10]}-{self.value[10:]}"
        return self.value


@dataclass(frozen=True)
class Percentage(ValueObject):
    value: Decimal

    def _validate(self):
        if not isinstance(self.value, Decimal):
            raise ValueError("value must be a Decimal")
        if self.value < 0 or self.value > 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {self.value}")

    def as_decimal(self) -> Decimal:
        return self.value / Decimal("100")

    def apply_to(self, money: Money) -> Money:
        return money * self.as_decimal()
