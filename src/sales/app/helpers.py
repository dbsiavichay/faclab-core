from decimal import Decimal


def recalculate_sale_totals(sale, items) -> None:
    """Recalcula subtotal y total de la venta a partir de sus items"""
    subtotal = sum(item.subtotal for item in items)

    # Aplicar descuento general si existe
    discount_amount = subtotal * (sale.discount / Decimal("100"))
    subtotal_after_discount = subtotal - discount_amount

    # Calcular impuestos
    tax_amount = subtotal_after_discount * (sale.tax / Decimal("100"))

    sale.subtotal = subtotal
    sale.total = subtotal_after_discount + tax_amount
