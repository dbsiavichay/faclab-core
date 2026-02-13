from datetime import datetime
from decimal import Decimal

import pytest

from src.sales.domain.entities import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    Sale,
    SaleItem,
    SaleStatus,
)
from src.sales.domain.exceptions import InvalidSaleStatusError


def test_sale_item_subtotal_calculation():
    """Test que el subtotal se calcula correctamente"""
    item = SaleItem(
        sale_id=1,
        product_id=1,
        quantity=10,
        unit_price=Decimal("100.00"),
        discount=Decimal("10"),  # 10%
    )
    # Subtotal = (10 * 100) - (1000 * 10/100) = 1000 - 100 = 900
    assert item.subtotal == Decimal("900.00")


def test_sale_item_subtotal_no_discount():
    """Test subtotal sin descuento"""
    item = SaleItem(
        sale_id=1,
        product_id=1,
        quantity=5,
        unit_price=Decimal("50.00"),
        discount=Decimal("0"),
    )
    assert item.subtotal == Decimal("250.00")


def test_sale_confirm_changes_status():
    """Test que confirmar una venta cambia su estado"""
    sale = Sale(customer_id=1, status=SaleStatus.DRAFT)
    sale.confirm()
    assert sale.status == SaleStatus.CONFIRMED
    assert sale.sale_date is not None


def test_sale_confirm_only_draft():
    """Test que solo se pueden confirmar ventas en DRAFT"""
    sale = Sale(customer_id=1, status=SaleStatus.CONFIRMED)
    with pytest.raises(InvalidSaleStatusError):
        sale.confirm()


def test_sale_cancel_from_draft():
    """Test cancelar una venta en DRAFT"""
    sale = Sale(customer_id=1, status=SaleStatus.DRAFT)
    sale.cancel()
    assert sale.status == SaleStatus.CANCELLED


def test_sale_cancel_from_confirmed():
    """Test cancelar una venta confirmada"""
    sale = Sale(customer_id=1, status=SaleStatus.CONFIRMED)
    sale.cancel()
    assert sale.status == SaleStatus.CANCELLED


def test_sale_cancel_from_invoiced_fails():
    """Test que no se pueden cancelar ventas facturadas"""
    sale = Sale(customer_id=1, status=SaleStatus.INVOICED)
    with pytest.raises(InvalidSaleStatusError):
        sale.cancel()


def test_sale_invoice_only_confirmed():
    """Test que solo se pueden facturar ventas confirmadas"""
    sale = Sale(customer_id=1, status=SaleStatus.CONFIRMED)
    sale.invoice()
    assert sale.status == SaleStatus.INVOICED


def test_sale_invoice_draft_fails():
    """Test que no se pueden facturar ventas en DRAFT"""
    sale = Sale(customer_id=1, status=SaleStatus.DRAFT)
    with pytest.raises(InvalidSaleStatusError):
        sale.invoice()


def test_sale_update_payment_status_pending():
    """Test actualizar estado de pago a PENDING"""
    sale = Sale(customer_id=1, total=Decimal("1000"))
    sale.update_payment_status(Decimal("0"))
    assert sale.payment_status == PaymentStatus.PENDING


def test_sale_update_payment_status_partial():
    """Test actualizar estado de pago a PARTIAL"""
    sale = Sale(customer_id=1, total=Decimal("1000"))
    sale.update_payment_status(Decimal("500"))
    assert sale.payment_status == PaymentStatus.PARTIAL


def test_sale_update_payment_status_paid():
    """Test actualizar estado de pago a PAID"""
    sale = Sale(customer_id=1, total=Decimal("1000"))
    sale.update_payment_status(Decimal("1000"))
    assert sale.payment_status == PaymentStatus.PAID


def test_sale_update_payment_status_overpaid():
    """Test actualizar estado de pago cuando se paga de más"""
    sale = Sale(customer_id=1, total=Decimal("1000"))
    sale.update_payment_status(Decimal("1500"))
    assert sale.payment_status == PaymentStatus.PAID


def test_payment_validates_positive_amount():
    """Test que Payment valida que el monto sea positivo"""
    with pytest.raises(ValueError, match="Payment amount must be positive"):
        Payment(
            sale_id=1,
            amount=Decimal("-100"),
            payment_method=PaymentMethod.CASH,
        )


def test_payment_validates_zero_amount():
    """Test que Payment no acepta monto cero"""
    with pytest.raises(ValueError, match="Payment amount must be positive"):
        Payment(
            sale_id=1,
            amount=Decimal("0"),
            payment_method=PaymentMethod.CASH,
        )


def test_payment_sets_default_date():
    """Test que Payment establece fecha por defecto"""
    payment = Payment(
        sale_id=1,
        amount=Decimal("100"),
        payment_method=PaymentMethod.CASH,
    )
    assert payment.payment_date is not None
    assert isinstance(payment.payment_date, datetime)
