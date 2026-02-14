from unittest.mock import MagicMock

from src.customers.app.queries.customer import (
    GetAllCustomersQuery,
    GetAllCustomersQueryHandler,
    GetCustomerByIdQuery,
    GetCustomerByIdQueryHandler,
    GetCustomerByTaxIdQuery,
    GetCustomerByTaxIdQueryHandler,
)
from src.customers.domain.entities import Customer, TaxType


def _make_customer(**overrides) -> Customer:
    defaults = {
        "id": 1,
        "name": "Test Customer",
        "tax_id": "1234567890123",
        "tax_type": TaxType.RUC,
        "is_active": True,
    }
    defaults.update(overrides)
    return Customer(**defaults)


def test_get_all_customers_query_handler():
    customers = [_make_customer(id=1), _make_customer(id=2, name="Second")]
    repo = MagicMock()
    repo.get_all.return_value = customers
    handler = GetAllCustomersQueryHandler(repo)

    result = handler.handle(GetAllCustomersQuery())

    assert len(result) == 2
    assert result[0]["name"] == "Test Customer"
    assert result[1]["name"] == "Second"


def test_get_customer_by_id_handler():
    customer = _make_customer()
    repo = MagicMock()
    repo.get_by_id.return_value = customer
    handler = GetCustomerByIdQueryHandler(repo)

    result = handler.handle(GetCustomerByIdQuery(id=1))

    assert result is not None
    assert result["id"] == 1
    assert result["name"] == "Test Customer"


def test_get_customer_by_id_not_found_returns_none():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    handler = GetCustomerByIdQueryHandler(repo)

    result = handler.handle(GetCustomerByIdQuery(id=999))

    assert result is None


def test_get_customer_by_tax_id_handler():
    customer = _make_customer()
    repo = MagicMock()
    repo.first.return_value = customer
    handler = GetCustomerByTaxIdQueryHandler(repo)

    result = handler.handle(GetCustomerByTaxIdQuery(tax_id="1234567890123"))

    assert result is not None
    assert result["tax_id"] == "1234567890123"
