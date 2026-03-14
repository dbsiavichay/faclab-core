from decimal import Decimal


def recalculate_sale_totals(sale, items) -> None:
    """Recalcula subtotal, tax, discount y total de la venta a partir de sus items"""
    subtotal = sum(item.subtotal for item in items)
    tax = sum(item.tax_amount for item in items)

    if sale.discount_type == "PERCENTAGE":
        discount = subtotal * sale.discount_value / Decimal("100")
    elif sale.discount_type == "AMOUNT":
        discount = sale.discount_value
    else:
        discount = Decimal("0")

    sale.subtotal = subtotal
    sale.tax = tax
    sale.discount = discount
    sale.total = subtotal + tax - discount
