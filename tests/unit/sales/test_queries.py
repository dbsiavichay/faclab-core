from decimal import Decimal
from unittest.mock import MagicMock

from src.sales.app.queries import (
    GetAllSalesQuery,
    GetAllSalesQueryHandler,
    GetSaleByIdQuery,
    GetSaleByIdQueryHandler,
    GetSaleItemsQuery,
    GetSaleItemsQueryHandler,
    GetSalePaymentsQuery,
    GetSalePaymentsQueryHandler,
)
from src.sales.domain.entities import Payment, PaymentMethod, Sale, SaleItem, SaleStatus


def _make_sale(**overrides) -> Sale:
    defaults = {
        "id": 1,
        "customer_id": 10,
        "status": SaleStatus.DRAFT,
        "subtotal": Decimal("0"),
        "total": Decimal("0"),
    }
    defaults.update(overrides)
    return Sale(**defaults)


def _make_sale_item(**overrides) -> SaleItem:
    defaults = {
        "id": 1,
        "sale_id": 1,
        "product_id": 100,
        "quantity": 10,
        "unit_price": Decimal("100.00"),
        "discount": Decimal("0"),
    }
    defaults.update(overrides)
    return SaleItem(**defaults)


def _make_payment(**overrides) -> Payment:
    defaults = {
        "id": 1,
        "sale_id": 1,
        "amount": Decimal("500.00"),
        "payment_method": PaymentMethod.CASH,
    }
    defaults.update(overrides)
    return Payment(**defaults)


def _mock_repo(entity=None, entities=None):
    repo = MagicMock()
    if entity is not None:
        repo.get_by_id.return_value = entity
    if entities is not None:
        repo.filter_by.return_value = entities
        repo.get_all.return_value = entities
    return repo


def test_get_all_sales_query_handler():
    """Test obtener todas las ventas"""
    sales = [
        _make_sale(id=1, customer_id=10),
        _make_sale(id=2, customer_id=20),
    ]
    repo = _mock_repo(entities=sales)
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery()
    result = handler.handle(query)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


def test_get_all_sales_with_customer_filter():
    """Test filtrar ventas por cliente"""
    sales = [_make_sale(id=1, customer_id=10)]
    repo = _mock_repo(entities=sales)
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery(customer_id=10)
    result = handler.handle(query)

    repo.filter_by.assert_called_once()
    assert len(result) == 1
    assert result[0]["customer_id"] == 10


def test_get_all_sales_with_status_filter():
    """Test filtrar ventas por estado"""
    sales = [_make_sale(id=1, status=SaleStatus.CONFIRMED)]
    repo = _mock_repo(entities=sales)
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery(status="CONFIRMED")
    result = handler.handle(query)

    repo.filter_by.assert_called_once()
    assert len(result) == 1


def test_get_all_sales_with_pagination():
    """Test paginación de ventas"""
    sales = [_make_sale(id=i) for i in range(1, 11)]
    repo = _mock_repo(entities=sales[:5])  # Simular primera página
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery(limit=5, offset=0)
    result = handler.handle(query)

    assert len(result) == 5


def test_get_all_sales_empty():
    """Test obtener ventas cuando no hay ninguna"""
    repo = _mock_repo(entities=[])
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery()
    result = handler.handle(query)

    assert len(result) == 0


def test_get_sale_by_id_query_handler():
    """Test obtener una venta por ID"""
    sale = _make_sale(id=1, customer_id=10)
    repo = _mock_repo(entity=sale)
    handler = GetSaleByIdQueryHandler(repo)

    query = GetSaleByIdQuery(sale_id=1)
    result = handler.handle(query)

    repo.get_by_id.assert_called_once_with(1)
    assert result is not None
    assert result["id"] == 1
    assert result["customer_id"] == 10


def test_get_sale_by_id_not_found():
    """Test obtener una venta que no existe"""
    repo = _mock_repo()
    repo.get_by_id.return_value = None
    handler = GetSaleByIdQueryHandler(repo)

    query = GetSaleByIdQuery(sale_id=999)
    result = handler.handle(query)

    assert result is None


def test_get_sale_items_query_handler():
    """Test obtener items de una venta"""
    items = [
        _make_sale_item(id=1, product_id=100, quantity=10),
        _make_sale_item(id=2, product_id=200, quantity=5),
    ]
    repo = _mock_repo(entities=items)
    handler = GetSaleItemsQueryHandler(repo)

    query = GetSaleItemsQuery(sale_id=1)
    result = handler.handle(query)

    repo.filter_by.assert_called_once_with(sale_id=1)
    assert len(result) == 2
    assert result[0]["product_id"] == 100
    assert result[1]["product_id"] == 200


def test_get_sale_items_empty():
    """Test obtener items de una venta sin items"""
    repo = _mock_repo(entities=[])
    handler = GetSaleItemsQueryHandler(repo)

    query = GetSaleItemsQuery(sale_id=1)
    result = handler.handle(query)

    assert len(result) == 0


def test_get_sale_payments_query_handler():
    """Test obtener pagos de una venta"""
    payments = [
        _make_payment(id=1, amount=Decimal("500.00")),
        _make_payment(id=2, amount=Decimal("300.00")),
    ]
    repo = _mock_repo(entities=payments)
    handler = GetSalePaymentsQueryHandler(repo)

    query = GetSalePaymentsQuery(sale_id=1)
    result = handler.handle(query)

    repo.filter_by.assert_called_once_with(sale_id=1)
    assert len(result) == 2
    assert result[0]["amount"] == Decimal("500.00")
    assert result[1]["amount"] == Decimal("300.00")


def test_get_sale_payments_empty():
    """Test obtener pagos de una venta sin pagos"""
    repo = _mock_repo(entities=[])
    handler = GetSalePaymentsQueryHandler(repo)

    query = GetSalePaymentsQuery(sale_id=1)
    result = handler.handle(query)

    assert len(result) == 0


def test_get_all_sales_multiple_filters():
    """Test filtrar ventas con múltiples criterios"""
    sales = [_make_sale(id=1, customer_id=10, status=SaleStatus.CONFIRMED)]
    repo = _mock_repo(entities=sales)
    handler = GetAllSalesQueryHandler(repo)

    query = GetAllSalesQuery(customer_id=10, status="CONFIRMED", limit=10)
    handler.handle(query)

    # Verificar que se aplicaron los filtros
    call_kwargs = repo.filter_by.call_args[1]
    assert call_kwargs["customer_id"] == 10
    assert call_kwargs["status"] == "CONFIRMED"
    assert call_kwargs["limit"] == 10
