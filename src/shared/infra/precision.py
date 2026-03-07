"""Centralized numeric precision constants for database columns."""

from sqlalchemy import Numeric

# Monetary values: prices, costs, subtotals, taxes, totals, amounts, credit limits
# Precision 12 = up to 999,999.999999 (6 integer digits + 6 decimal digits)
# Scale 6 = 6 decimal places for calculation accuracy
MONEY_PRECISION = 12
MONEY_SCALE = 6
MoneyColumn = Numeric(MONEY_PRECISION, MONEY_SCALE)

# Percentages: discounts, tax rates
# Precision 5 = up to 999.99 (3 integer digits + 2 decimal digits)
# Scale 2 = 2 decimal places (e.g., 12.50%, 33.33%)
PERCENTAGE_PRECISION = 5
PERCENTAGE_SCALE = 2
PercentageColumn = Numeric(PERCENTAGE_PRECISION, PERCENTAGE_SCALE)
