from decimal import Decimal

import pytest

from src.shared.domain.value_objects import Email, Money, Percentage, TaxId


class TestMoney:
    def test_creation(self):
        m = Money(amount=Decimal("10.00"), currency="USD")
        assert m.amount == Decimal("10.00")
        assert m.currency == "USD"

    def test_add(self):
        a = Money(amount=Decimal("10.00"), currency="USD")
        b = Money(amount=Decimal("5.50"), currency="USD")
        result = a + b
        assert result.amount == Decimal("15.50")

    def test_sub(self):
        a = Money(amount=Decimal("10.00"), currency="USD")
        b = Money(amount=Decimal("3.00"), currency="USD")
        result = a - b
        assert result.amount == Decimal("7.00")

    def test_mul(self):
        m = Money(amount=Decimal("10.00"), currency="USD")
        result = m * Decimal("3")
        assert result.amount == Decimal("30.00")

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            Money(amount=Decimal("-1"), currency="USD")

    def test_currency_mismatch_add_raises(self):
        a = Money(amount=Decimal("10.00"), currency="USD")
        b = Money(amount=Decimal("5.00"), currency="EUR")
        with pytest.raises(ValueError, match="Cannot add"):
            a + b

    def test_currency_mismatch_sub_raises(self):
        a = Money(amount=Decimal("10.00"), currency="USD")
        b = Money(amount=Decimal("5.00"), currency="EUR")
        with pytest.raises(ValueError, match="Cannot subtract"):
            a - b


class TestEmail:
    def test_valid(self):
        email = Email(value="user@example.com")
        assert email.value == "user@example.com"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            Email(value="not-an-email")


class TestTaxId:
    _error_match = "Invalid tax ID"

    def test_valid_ruc(self):
        tax_id = TaxId(value="1710034065001")
        assert tax_id.value == "1710034065001"

    def test_valid_cedula(self):
        tax_id = TaxId(value="1710034065")
        assert tax_id.value == "1710034065"

    def test_invalid_length_raises(self):
        with pytest.raises(ValueError, match=self._error_match):
            TaxId(value="12345")

    def test_non_digit_raises(self):
        with pytest.raises(ValueError, match=self._error_match):
            TaxId(value="17ABC34065")

    def test_invalid_province_raises(self):
        with pytest.raises(ValueError, match="Invalid ID or RUC"):
            TaxId(value="9910034065")

    def test_invalid_check_digit_raises(self):
        with pytest.raises(ValueError, match="Invalid ID or RUC"):
            TaxId(value="1710034060")


class TestPercentage:
    def test_valid_range(self):
        p = Percentage(value=Decimal("15"))
        assert p.value == Decimal("15")

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="between 0 and 100"):
            Percentage(value=Decimal("101"))

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="between 0 and 100"):
            Percentage(value=Decimal("-1"))

    def test_as_decimal(self):
        p = Percentage(value=Decimal("25"))
        assert p.as_decimal() == Decimal("0.25")

    def test_apply_to(self):
        p = Percentage(value=Decimal("10"))
        m = Money(amount=Decimal("200.00"), currency="USD")
        result = p.apply_to(m)
        assert result.amount == Decimal("20.0000")
        assert result.currency == "USD"
