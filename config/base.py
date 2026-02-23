from dataclasses import dataclass

from environs import Env

env = Env()


@dataclass
class OpenTelemetryConfig:
    service_name: str
    otlp_endpoint: str
    environment: str
    enabled: bool = True
    sampling_rate: float = 1.0


@dataclass
class DocsConfig:
    title: str
    version: str
    description: str
    openapi_tags: list[dict]
    tag_groups: list[dict]
    enabled: bool = True


class BaseConfig:
    SERVICE_NAME = env("SERVICE_NAME", "faclab-core")
    ENVIRONMENT = env("ENVIRONMENT", "local")

    #
    # Logging config
    #
    LOG_LEVEL = env("LOG_LEVEL", "INFO")

    #
    # Database config
    #
    DB_CONNECTION_STRING = env("DATABASE_URL", "sqlite:///./warehouse.db")

    #
    # OpenTelemetry config
    #
    OTEL_OTLP_ENDPOINT = env("OTEL_OTLP_ENDPOINT", "http://localhost:4317")
    OTEL_SERVICE_NAME = env("OTEL_SERVICE_NAME", SERVICE_NAME)
    OTEL_ENVIRONMENT = env("OTEL_ENVIRONMENT", ENVIRONMENT)
    OTEL_ENABLED = env.bool("OTEL_ENABLED", True)
    OTEL_SAMPLING_RATE = env.float("OTEL_SAMPLING_RATE", 1.0)

    #
    # Docs config
    #
    DOCS_ENABLED = env.bool("DOCS_ENABLED", True)

    API_TITLE = "Faclab Core API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
Faclab Core is a sales and inventory management API.

## API Surfaces

| Surface | Base path | Purpose |
|---------|-----------|---------|
| **Admin** | `/api/admin` | Back-office: catalog, inventory, customers, sales reporting |
| **POS** | `/api/pos` | Point-of-sale: product lookup, customer search, full sales lifecycle |

## Error format

```json
{
  "error_code": "DOMAIN_ERROR",
  "message": "Human-readable description",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid",
  "detail": {}
}
```
"""

    API_OPENAPI_TAGS: list[dict] = [
        # Admin — Catalog
        {
            "name": "admin - categories",
            "description": "Organize the product catalog with a structured category system.",
        },
        {
            "name": "admin - units of measure",
            "description": "Manage units of measure used across products (e.g., kg, liters, units, boxes).",
        },
        {
            "name": "admin - products",
            "description": (
                "Full product catalog management: SKU, pricing, categorization, "
                "stock thresholds, and service flags."
            ),
        },
        # Admin — Inventory
        {
            "name": "admin - warehouses",
            "description": "Manage physical warehouse facilities where inventory is stored.",
        },
        {
            "name": "admin - locations",
            "description": "Manage specific storage locations within warehouses — shelves, bins, and zones.",
        },
        {
            "name": "admin - stock",
            "description": "Query real-time stock levels per product and storage location.",
        },
        {
            "name": "admin - movements",
            "description": (
                "Record and query inventory movements (IN/OUT). Includes manual entries "
                "and system-generated movements from confirmed or cancelled sales."
            ),
        },
        # Admin — Customers
        {
            "name": "admin - customers",
            "description": (
                "Manage customer profiles: tax ID (RUC), credit limits, payment terms, "
                "and activation status."
            ),
        },
        {
            "name": "admin - customer-contacts",
            "description": "Manage individual contacts associated with a customer.",
        },
        # Admin — Suppliers
        {
            "name": "admin - suppliers",
            "description": (
                "Manage supplier profiles: tax ID, payment terms, lead times, "
                "and activation status."
            ),
        },
        {
            "name": "admin - supplier-contacts",
            "description": "Manage individual contacts associated with a supplier.",
        },
        {
            "name": "admin - supplier-products",
            "description": (
                "Manage the purchase catalog: link products to suppliers with "
                "purchase price, supplier SKU, and minimum order quantity."
            ),
        },
        # Admin — Lots & Serials
        {
            "name": "admin - lots",
            "description": "Lot management — expiry tracking, lot quantities, and perishable product control.",
        },
        {
            "name": "admin - serials",
            "description": "Serial number tracking — unit-level traceability for electronics and equipment.",
        },
        # Admin — Purchasing
        {
            "name": "admin - purchase-orders",
            "description": "Manage purchase orders: create, send to supplier, receive goods, and cancel.",
        },
        {
            "name": "admin - purchase-order-items",
            "description": "Manage line items within a purchase order.",
        },
        # Admin — Adjustments
        {
            "name": "admin - adjustments",
            "description": "Manage inventory adjustments — physical counts, corrections, write-offs, and expiration entries.",
        },
        {
            "name": "admin - adjustment-items",
            "description": "Manage individual line items within an inventory adjustment.",
        },
        # Admin — Transfers
        {
            "name": "admin - transfers",
            "description": "Manage stock transfers between warehouse locations.",
        },
        {
            "name": "admin - transfer-items",
            "description": "Manage individual line items within a stock transfer.",
        },
        # Admin — Sales
        {
            "name": "admin - sales",
            "description": "Read-only access to all sales data for back-office reporting and auditing.",
        },
        # POS
        {
            "name": "pos - products",
            "description": "Product lookup for point-of-sale operations.",
        },
        {
            "name": "pos - customers",
            "description": "Customer lookup for point-of-sale, including search by tax ID (RUC).",
        },
        {
            "name": "pos - sales",
            "description": (
                "Full sales lifecycle for the point-of-sale terminal: "
                "create, add items, confirm, cancel, and register payments."
            ),
        },
    ]

    API_TAG_GROUPS: list[dict] = [
        {
            "name": "Admin — Catalog",
            "tags": [
                "admin - categories",
                "admin - units of measure",
                "admin - products",
            ],
        },
        {
            "name": "Admin — Inventory",
            "tags": [
                "admin - warehouses",
                "admin - locations",
                "admin - stock",
                "admin - movements",
            ],
        },
        {
            "name": "Admin — Lots & Serials",
            "tags": ["admin - lots", "admin - serials"],
        },
        {
            "name": "Admin — Customers",
            "tags": ["admin - customers", "admin - customer-contacts"],
        },
        {
            "name": "Admin — Suppliers",
            "tags": [
                "admin - suppliers",
                "admin - supplier-contacts",
                "admin - supplier-products",
            ],
        },
        {
            "name": "Admin — Purchasing",
            "tags": ["admin - purchase-orders", "admin - purchase-order-items"],
        },
        {
            "name": "Admin — Adjustments",
            "tags": ["admin - adjustments", "admin - adjustment-items"],
        },
        {
            "name": "Admin — Transfers",
            "tags": ["admin - transfers", "admin - transfer-items"],
        },
        {
            "name": "Admin — Sales",
            "tags": ["admin - sales"],
        },
        {
            "name": "POS",
            "tags": ["pos - products", "pos - customers", "pos - sales"],
        },
    ]

    def get_otel_config(self) -> OpenTelemetryConfig:
        return OpenTelemetryConfig(
            service_name=self.OTEL_SERVICE_NAME,
            otlp_endpoint=self.OTEL_OTLP_ENDPOINT,
            environment=self.OTEL_ENVIRONMENT,
            enabled=self.OTEL_ENABLED,
            sampling_rate=self.OTEL_SAMPLING_RATE,
        )

    def get_docs_config(self) -> DocsConfig:
        return DocsConfig(
            title=self.API_TITLE,
            version=self.API_VERSION,
            description=self.API_DESCRIPTION,
            openapi_tags=self.API_OPENAPI_TAGS,
            tag_groups=self.API_TAG_GROUPS,
            enabled=self.DOCS_ENABLED,
        )
