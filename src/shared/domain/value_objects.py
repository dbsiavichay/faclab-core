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

    _ERROR_MSG = (
        "Invalid tax ID: {value}. "
        "Must be a valid Ecuadorian ID (10 digits) or RUC (13 digits)."
    )
    _INVALID_ID_MSG = "Invalid ID or RUC: {value}. The number does not match a valid Ecuadorian ID or RUC."

    def _validate(self):
        if not isinstance(self.value, str) or not self.value.isdigit():
            raise ValueError(self._ERROR_MSG.format(value=self.value))

        if len(self.value) not in (10, 13):
            raise ValueError(self._ERROR_MSG.format(value=self.value))

        self._validate_algorithm()

    def _validate_algorithm(self):
        code = self.value
        province_code = int(code[:2])
        if province_code not in range(1, 25) and province_code != 30:
            raise ValueError(self._INVALID_ID_MSG.format(value=self.value))

        third_digit = int(code[2])
        is_public = len(code) == 13 and third_digit == 6
        is_private = len(code) == 13 and third_digit == 9
        is_natural = not (is_public or is_private)
        base = 10 if is_natural else 11

        if is_public:
            coefficients = (3, 2, 7, 6, 5, 4, 3, 2)
        elif is_private:
            coefficients = (4, 3, 2, 7, 6, 5, 4, 3, 2)
        else:
            coefficients = (2, 1, 2, 1, 2, 1, 2, 1, 2)

        checker = int(code[len(coefficients)])
        total = 0

        for i, coeff in enumerate(coefficients):
            product = int(code[i]) * coeff
            if is_natural:
                total += product if product < 10 else (product // 10) + (product % 10)
            else:
                total += product

        remainder = total % base
        result = base - remainder if remainder != 0 else 0

        if result != checker:
            raise ValueError(self._INVALID_ID_MSG.format(value=self.value))


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
