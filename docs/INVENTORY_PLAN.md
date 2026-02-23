# Plan de Desarrollo: Sistema de Inventarios Completo

**Proyecto:** Faclab Core
**Stack:** FastAPI + SQLAlchemy + Wireup DI + Clean Architecture + CQRS
**Fecha inicio:** 2026-02-21
**Módulo excluido:** POS / Ventas (desarrollo posterior)

---

## Estado Actual del Sistema

### Lo que ya existe (NO tocar sin razón)

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| `src/shared/` | Completo | Domain primitives, CQRS bases, EventBus, Mappers, BaseRepository |
| `src/catalog/product/` | Básico | `Category` (id, name, desc) + `Product` (id, name, sku, desc, category_id) |
| `src/inventory/stock/` | Básico | `Stock` (id, product_id, quantity, location: str) |
| `src/inventory/movement/` | Básico | `Movement` (id, product_id, quantity, type IN/OUT, reason, date) |
| `src/customers/` | Completo | Full CQRS, TaxId VO, activación, contactos |
| `src/sales/` | Completo | DRAFT→CONFIRMED→INVOICED→CANCELLED, pagos |
| `src/pos/` | Básico | Confirm/Cancel atómico con inventario |

### Convenciones del proyecto (OBLIGATORIAS en todo el plan)

1. **Entidades**: `@dataclass` extendiendo `Entity`, inmutables, usar `replace()` para modificar
2. **Comandos**: `@dataclass` extendiendo `Command`, handler extendiendo `CommandHandler[Cmd, Result]`
3. **Queries**: `@dataclass` extendiendo `Query`, handler extendiendo `QueryHandler[Q, Result]`
4. **Eventos**: `@dataclass` extendiendo `DomainEvent`, `_payload()` abstracto, publicar via `EventPublisher`
5. **Repositorios**: extender `SqlAlchemyRepository[E]`, declarar `__model__`, registrar `@injectable(lifetime="scoped", as_type=Repository[E])`
6. **Mappers**: extender `Mapper[E, M]`, declarar `__entity__` + `__exclude_fields__`, registrar `@injectable` (singleton)
7. **DI**: registrar en `container.py` de cada módulo, importar en `src/container.py`
8. **Rutas**: registrar en `main.py`
9. **Migraciones**: `make migrations m="descripción"` + `make upgrade`
10. **Linter**: ruff (NO black/flake8/isort)
11. **Commits**: conventional commits (`feat:`, `fix:`, `refactor:`, `test:`)

### Estructura de archivos por módulo (plantilla estándar)

```
src/nuevo_modulo/
├── domain/
│   ├── entities.py       # Dataclasses extendiendo Entity
│   ├── events.py         # DomainEvent subclasses (si aplica)
│   ├── specifications.py # Specification subclasses (si aplica)
│   └── exceptions.py     # DomainError subclasses (si aplica)
├── app/
│   ├── commands/         # CommandHandler implementations
│   ├── queries/          # QueryHandler implementations
│   └── types.py          # TypedDicts para I/O de handlers
└── infra/
    ├── models.py         # SQLAlchemy models extendiendo Base
    ├── mappers.py        # Mapper declarations
    ├── repositories.py   # Repository factory functions
    ├── routes.py         # FastAPI APIRouter
    ├── validators.py     # Pydantic Request/Response schemas
    ├── container.py      # INJECTABLES list
    └── controllers.py    # (opcional, si la lógica de routing es compleja)
```

---

## Visión del Sistema Completo

```
┌─────────────────────────────────────────────────────────┐
│                    SISTEMA DE INVENTARIOS               │
├────────────────┬───────────────────────────────────────┤
│   CATÁLOGO     │  PROVEEDORES & COMPRAS                 │
│ • UoM          │  • Suppliers + Contacts                │
│ • Categorías   │  • Purchase Orders (DRAFT→RECEIVED)    │
│ • Productos    │  • Purchase Receipts                   │
│   (mejorado)   │                                        │
├────────────────┼───────────────────────────────────────┤
│  ALMACENES     │  INVENTARIO CORE                       │
│ • Warehouses   │  • Stock multi-ubicación               │
│ • Locations    │  • Movimientos mejorados               │
│ • Zonas        │  • Lotes & Seriales                    │
│                │  • Transferencias                       │
├────────────────┼───────────────────────────────────────┤
│  AJUSTES       │  REPORTES & ALERTAS                    │
│ • Conteos      │  • Valoración de inventario            │
│   físicos      │  • Rotación de productos               │
│ • Ajustes      │  • Alertas de stock bajo               │
│   manuales     │  • Historial de movimientos            │
└────────────────┴───────────────────────────────────────┘
```

---

## FASE 1: Catálogo Mejorado (Productos + UoM) ✅ COMPLETADA (2026-02-22)

**Objetivo:** Enriquecer el catálogo para soportar el inventario completo.
**Impacto en BD:** Migración `ALTER TABLE products`, nueva tabla `units_of_measure`.
**Migración aplicada:** `342b2ecf1258_create_units_of_measure_table_and_.py`

### 1.1 Unidades de Medida (`src/catalog/uom/`)

Nueva entidad:
```python
@dataclass
class UnitOfMeasure(Entity):
    name: str                    # "Kilogramo", "Unidad", "Caja"
    symbol: str                  # "kg", "un", "cj"
    id: int | None = None
    description: str | None = None
    is_active: bool = True
```

Tabla: `units_of_measure` (id, name, symbol, description, is_active)

Handlers:
- Commands: Create, Update, Delete
- Queries: GetAll, GetById

Ruta: `GET/POST /api/admin/units-of-measure`

### 1.2 Producto Mejorado

Campos a agregar a `Product`:
```python
@dataclass
class Product(Entity):
    # Existentes:
    name: str
    sku: str
    id: int | None = None
    description: str | None = None
    category_id: int | None = None
    created_at: datetime | None = None

    # NUEVOS:
    barcode: str | None = None          # EAN-13, QR, etc.
    purchase_price: Decimal | None = None  # Costo de compra
    sale_price: Decimal | None = None      # Precio de venta sugerido
    unit_of_measure_id: int | None = None  # FK → units_of_measure
    is_active: bool = True
    is_service: bool = False               # Servicios no manejan stock
    min_stock: int = 0                     # Stock mínimo (alerta)
    max_stock: int | None = None           # Stock máximo (alerta)
    reorder_point: int = 0                 # Punto de reorden
    lead_time_days: int | None = None      # Días de reabastecimiento
```

Migración: `make migrations m="enhance products with pricing and stock controls"`

### 1.3 Checklist Fase 1

- [x] Crear `src/catalog/uom/` con estructura completa
- [x] Crear `UnitOfMeasureModel` en `infra/models.py`
- [x] Crear mapper, repository, handlers (Create/Update/Delete/GetAll/GetById)
- [x] Crear routes en `/api/admin/units-of-measure`
- [x] Registrar en `src/container.py` y `main.py`
- [x] Actualizar `Product` entity con nuevos campos
- [x] Actualizar `ProductModel` con nuevas columnas
- [x] Actualizar `ProductMapper` con `__exclude_fields__` (created_at)
- [x] Actualizar validators de Product (nuevos campos + aliases camelCase)
- [x] Crear migración y aplicar (`342b2ecf1258`)
- [x] Actualizar `alembic/env.py` con todos los modelos (incluye CustomerModel)

### 1.4 Notas de implementación (para sesiones futuras)

- Migración de columnas `NOT NULL` sobre tabla con datos requiere `server_default` en la migración — Alembic autogenerate NO lo agrega automáticamente. Editar manualmente antes de `make upgrade`.
- `alembic/env.py` debe importar TODOS los modelos para que Alembic resuelva FKs entre tablas. Se agregaron `CustomerModel`, `CustomerContactModel` y `UnitOfMeasureModel`.
- Validators de Product migraron a `ConfigDict(alias_generator=to_camel, populate_by_name=True)` — es más limpio que `AliasChoices` cuando hay muchos campos.
- `model_dump(exclude_none=True)` en routes funciona correctamente con campos booleanos (`False` no es `None`).

---

## FASE 2: Almacenes y Ubicaciones ✅ COMPLETADA (2026-02-22)

**Objetivo:** Soporte multi-almacén con ubicaciones físicas dentro de cada almacén.
**Impacto en BD:** Nuevas tablas `warehouses`, `locations`. Stock pasa a ser por ubicación.
**Migración aplicada:** `49b16d5da943_phase_2_warehouses_locations_stock_.py`

### 2.1 Almacenes (`src/inventory/warehouse/`)

```python
@dataclass
class Warehouse(Entity):
    name: str
    code: str                    # Código único, ej: "ALM-01"
    id: int | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_active: bool = True
    is_default: bool = False     # Solo uno puede ser default
    manager: str | None = None
    phone: str | None = None
    email: str | None = None
    created_at: datetime | None = None
```

Tabla: `warehouses` (id, name, code UNIQUE, address, city, country, is_active, is_default, manager, phone, email, created_at)

### 2.2 Ubicaciones (`src/inventory/location/`)

```python
class LocationType(StrEnum):
    STORAGE = "storage"      # Almacenamiento regular
    RECEIVING = "receiving"  # Zona de recepción de mercancía
    SHIPPING = "shipping"    # Zona de despacho
    QUALITY = "quality"      # Control de calidad
    DAMAGED = "damaged"      # Mercancía dañada

@dataclass
class Location(Entity):
    warehouse_id: int
    name: str                    # "Pasillo A - Estante 1"
    code: str                    # "A-01-001"
    id: int | None = None
    type: LocationType = LocationType.STORAGE
    is_active: bool = True
    capacity: int | None = None  # Capacidad máxima (opcional)
```

Tabla: `locations` (id, warehouse_id FK, name, code, type, is_active, capacity)

### 2.3 Stock Multi-ubicación

Refactorizar `Stock` para ser por ubicación:
```python
@dataclass
class Stock(Entity):
    product_id: int
    location_id: int             # FK → locations (antes era location: str)
    quantity: int
    id: int | None = None
    reserved_quantity: int = 0   # Reservado para pedidos pendientes

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def update_quantity(self, delta: int) -> "Stock":
        new_qty = self.quantity + delta
        if new_qty < 0:
            raise DomainError("Stock no puede ser negativo")
        return replace(self, quantity=new_qty)
```

Tabla: `stocks` (id, product_id FK, location_id FK, quantity, reserved_quantity)
Constraint UNIQUE: (product_id, location_id)

### 2.4 Movimientos Mejorados

Agregar location a Movement:
```python
@dataclass
class Movement(Entity):
    product_id: int
    quantity: int
    type: MovementType
    # NUEVO:
    location_id: int | None = None     # Ubicación destino (IN) u origen (OUT)
    source_location_id: int | None = None  # Para transferencias
    reference_type: str | None = None  # "purchase_order", "sale", "adjustment", "transfer"
    reference_id: int | None = None    # ID del documento origen
    # Existentes:
    id: int | None = None
    reason: str | None = None
    date: datetime | None = None
    created_at: datetime | None = None
```

### 2.5 Checklist Fase 2

- [x] Crear `src/inventory/warehouse/` completo
- [x] Crear `src/inventory/location/` completo
- [x] Refactorizar `Stock` entity → `location_id` (reemplaza `location: str`), `reserved_quantity`, `available_quantity`, `update_quantity()` inmutable
- [x] Agregar `location_id`, `source_location_id`, `reference_type`, `reference_id` a `Movement`
- [x] Actualizar event handler `MovementCreated` → usa (product_id, location_id) para actualizar Stock
- [x] Actualizar `StockModel` (migration: rename location → location_id, add reserved_quantity, UNIQUE constraint)
- [x] Agregar `MovementModel` columnas nuevas (location_id, source_location_id, reference_type, reference_id)
- [x] Handlers: CRUD warehouses, CRUD locations, GetStock (filtrado por location_id/product_id)
- [x] Rutas: `/api/admin/warehouses`, `/api/admin/locations`, `/api/admin/stock`
- [x] Registrar en container y main.py
- [x] Migración y aplicar (`49b16d5da943`)
- [x] Tests: warehouse CRUD (13 tests), location CRUD (18 tests), stock entity (19 tests), event handlers actualizados

### 2.6 Notas de implementación (para sesiones futuras)

- `location_id` en Stock es opcional (`int | None`) para mantener compatibilidad con movimientos de ventas que no tienen ubicación asignada. Stock sin ubicación = stock "global" del producto.
- El event handler `handle_movement_created` busca stock por `(product_id, location_id)` — si `location_id=None`, busca el stock sin ubicación.
- `update_quantity()` ahora es inmutable: retorna un nuevo `Stock` con `replace()` en lugar de mutar `self.quantity`.
- `StockUpdated` y `StockCreated` events usan `location_id` en lugar de `location: str`.
- La migración agregó `server_default='0'` a `reserved_quantity` para compatibilidad con filas existentes.

---

## FASE 3: Gestión de Proveedores ✅ COMPLETADA (2026-02-22)

**Objetivo:** Registrar proveedores con sus contactos y catálogo de productos que suministran.
**Nuevo módulo:** `src/suppliers/`

### 3.1 Proveedor

```python
@dataclass
class Supplier(Entity):
    name: str
    tax_id: str
    id: int | None = None
    tax_type: TaxType = TaxType.RUC    # Reusar enum de customers
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    payment_terms: int | None = None   # Días de crédito
    lead_time_days: int | None = None  # Días de entrega promedio
    is_active: bool = True
    notes: str | None = None
    created_at: datetime | None = None
```

Tabla: `suppliers`

### 3.2 Contacto de Proveedor

```python
@dataclass
class SupplierContact(Entity):
    supplier_id: int
    name: str
    id: int | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
```

Tabla: `supplier_contacts` (FK → suppliers ON DELETE CASCADE)

### 3.3 Producto-Proveedor (Catálogo de compra)

```python
@dataclass
class SupplierProduct(Entity):
    supplier_id: int
    product_id: int
    purchase_price: Decimal
    id: int | None = None
    supplier_sku: str | None = None    # SKU del proveedor
    min_order_quantity: int = 1
    lead_time_days: int | None = None  # Sobreescribe el del proveedor
    is_preferred: bool = False         # Proveedor preferido para este producto
```

Tabla: `supplier_products` (FK → suppliers, products; UNIQUE: supplier_id + product_id)

### 3.4 Eventos

```python
@dataclass
class SupplierCreated(DomainEvent):
    supplier_id: int
    name: str
    tax_id: str

@dataclass
class SupplierActivated(DomainEvent):
    supplier_id: int

@dataclass
class SupplierDeactivated(DomainEvent):
    supplier_id: int
    reason: str | None
```

### 3.5 Checklist Fase 3

- [x] Crear `src/suppliers/` con estructura completa
- [x] Entities: `Supplier`, `SupplierContact`, `SupplierProduct`
- [x] Models: `SupplierModel`, `SupplierContactModel`, `SupplierProductModel`
- [x] Commands: Create/Update/Delete/Activate/Deactivate Supplier
- [x] Commands: Create/Update/Delete SupplierContact
- [x] Commands: Create/Update/Delete SupplierProduct (catálogo de compra)
- [x] Queries: GetAll/GetById Supplier, GetContacts, GetSupplierProducts, GetProductSuppliers
- [x] Rutas: `/api/admin/suppliers`, `/api/admin/suppliers/{id}/contacts`, `/api/admin/suppliers/{id}/products`
- [x] Eventos: SupplierCreated, SupplierActivated, SupplierDeactivated
- [x] Migración y aplicar (`94b429f1acba_create_suppliers_tables.py`)
- [x] Tests: CRUD supplier, contactos, catálogo de compra (32 tests, 100% pass)

**Completada:** 2026-02-22

### Notas de implementación Fase 3

- `TaxType` reutilizado de `src.customers.domain.entities` (no duplicado)
- `SupplierProduct` usa `UniqueConstraint("supplier_id", "product_id")` en el modelo
- Rutas anidadas en `SupplierRouter`: `/{supplier_id}/contacts` y `/{supplier_id}/products`
- Routers independientes: `SupplierContactRouter` y `SupplierProductRouter` para PUT/DELETE/GET por ID
- `SupplierProductRouter` incluye ruta `GET /by-product/{product_id}` para consultar todos los proveedores de un producto
- Migración aplicada: `94b429f1acba_create_suppliers_tables.py`

---

## FASE 4: Órdenes de Compra ✅ COMPLETADA (2026-02-22)

**Objetivo:** Gestionar el ciclo completo de compra desde la orden hasta la recepción.
**Nuevo módulo:** `src/purchasing/`
**Integración:** Al recibir mercancía → crea `Movement IN` → actualiza `Stock`

### 4.1 Ciclo de vida

```
DRAFT → SENT → PARTIAL_RECEIVED → RECEIVED
  ↓ (en cualquier estado antes de RECEIVED)
CANCELLED
```

### 4.2 Orden de Compra

```python
class PurchaseOrderStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"                      # Enviada al proveedor
    PARTIAL = "partial"                # Recepción parcial
    RECEIVED = "received"              # Completamente recibida
    CANCELLED = "cancelled"

@dataclass
class PurchaseOrder(Entity):
    supplier_id: int
    warehouse_id: int                  # Almacén destino
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    id: int | None = None
    order_number: str | None = None    # Generado automático: PO-2026-0001
    order_date: datetime | None = None
    expected_date: date | None = None
    notes: str | None = None
    subtotal: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    created_by: str | None = None
    created_at: datetime | None = None

    def send(self) -> "PurchaseOrder":
        if self.status != PurchaseOrderStatus.DRAFT:
            raise DomainError("Solo órdenes DRAFT pueden enviarse")
        return replace(self, status=PurchaseOrderStatus.SENT)

    def cancel(self) -> "PurchaseOrder":
        if self.status == PurchaseOrderStatus.RECEIVED:
            raise DomainError("No se puede cancelar una orden ya recibida")
        return replace(self, status=PurchaseOrderStatus.CANCELLED)

    def mark_partial(self) -> "PurchaseOrder":
        return replace(self, status=PurchaseOrderStatus.PARTIAL)

    def mark_received(self) -> "PurchaseOrder":
        return replace(self, status=PurchaseOrderStatus.RECEIVED)
```

### 4.3 Ítem de Orden de Compra

```python
@dataclass
class PurchaseOrderItem(Entity):
    purchase_order_id: int
    product_id: int
    quantity_ordered: int
    unit_cost: Decimal
    id: int | None = None
    quantity_received: int = 0
    notes: str | None = None

    @property
    def quantity_pending(self) -> int:
        return self.quantity_ordered - self.quantity_received

    @property
    def subtotal(self) -> Decimal:
        return self.unit_cost * self.quantity_ordered
```

### 4.4 Recepción de Mercancía

```python
@dataclass
class PurchaseReceipt(Entity):
    purchase_order_id: int
    received_by: str
    received_at: datetime
    id: int | None = None
    location_id: int | None = None     # Ubicación donde se almacena
    notes: str | None = None

@dataclass
class PurchaseReceiptItem(Entity):
    receipt_id: int
    purchase_order_item_id: int
    product_id: int
    quantity_received: int
    id: int | None = None
    location_id: int | None = None     # Puede ser diferente por ítem
    lot_number: str | None = None      # Para control de lotes (Fase 5)
```

### 4.5 Eventos

```python
@dataclass
class PurchaseOrderCreated(DomainEvent):
    purchase_order_id: int
    supplier_id: int
    order_number: str

@dataclass
class PurchaseOrderSent(DomainEvent):
    purchase_order_id: int
    supplier_id: int

@dataclass
class PurchaseOrderReceived(DomainEvent):
    purchase_order_id: int
    receipt_id: int
    items: list[dict]   # [{product_id, quantity, location_id}]
    is_complete: bool   # True si todas las cantidades recibidas

@dataclass
class PurchaseOrderCancelled(DomainEvent):
    purchase_order_id: int
    supplier_id: int
    reason: str | None
```

### 4.6 Flujo de integración con inventario

```
POST /api/admin/purchase-orders/{id}/receive
    → CreatePurchaseReceiptCommandHandler
        → Valida cantidades vs orden
        → Crea PurchaseReceipt + PurchaseReceiptItems
        → Actualiza quantity_received en PurchaseOrderItems
        → Cambia estado PO a PARTIAL o RECEIVED
        → Publica PurchaseOrderReceived event

@event_handler(PurchaseOrderReceived)
→ Para cada item en el evento:
    → Crear Movement(product_id, quantity, IN, location_id,
                     reference_type="purchase_order",
                     reference_id=purchase_order_id)
    → Event MovementCreated → actualiza Stock
```

### 4.7 Checklist Fase 4

- [x] Crear `src/purchasing/` con estructura completa
- [x] Entities: `PurchaseOrder`, `PurchaseOrderItem`, `PurchaseReceipt`, `PurchaseReceiptItem`
- [x] Models + Mappers + Repositories
- [x] Commands: CreatePO, UpdatePO, DeletePO (solo DRAFT), SendPO, CancelPO
- [x] Commands: AddPOItem, UpdatePOItem, RemovePOItem
- [x] Commands: CreatePurchaseReceipt (recepción con items, puede ser parcial)
- [x] Queries: GetAllPOs (filtros: status, supplier_id), GetPOById, GetPOItems, GetPOReceipts
- [x] Eventos y event handlers (PurchaseOrderReceived → crea Movements IN)
- [x] Generación automática de order_number (PO-YYYY-NNNN via `count_by_year()`)
- [x] Rutas: `/api/admin/purchase-orders`, `/api/admin/purchase-orders/{id}/items`, `/api/admin/purchase-orders/{id}/receive`
- [x] Migración y aplicar (`f5c7ea00ee81_create_purchase_orders_tables.py`)
- [x] Tests: 56 tests — entidades, eventos, comandos (incl. recepción parcial/completa), queries, event handler

**Completada:** 2026-02-22

### Notas de implementación Fase 4

- `PurchaseOrderStatus` usa `StrEnum` (igual que `SaleStatus`) para que `entity.dict()` retorne el valor string directamente
- `count_by_year(year)` en `PurchaseOrderRepository` usa `EXTRACT(year FROM created_at)` para generar el correlativo anual
- El event handler `handle_purchase_order_received` hace patch de `src.wireup_container` (no del módulo) — igual que los otros event handlers
- `PurchaseOrderItemResponse` no incluye `quantity_pending` ni `subtotal` (son properties calculadas, no almacenadas)
- Recepción parcial: si algún ítem tiene `quantity_pending > 0` después de la recepción, la PO pasa a `PARTIAL`; si todos quedan en 0, pasa a `RECEIVED`

---

## FASE 5: Lotes y Números de Serie ✅ COMPLETADA (2026-02-22)

**Objetivo:** Trazabilidad completa de mercancía por lote (farmacia, alimentos) o serial (electrónicos).
**Módulo:** Extender `src/inventory/`
**Migración aplicada:** `19e11200eb19_phase_5_lots_serial_numbers_and_.py`

### 5.1 Lotes (`src/inventory/lot/`)

```python
@dataclass
class Lot(Entity):
    product_id: int
    lot_number: str
    id: int | None = None
    manufacture_date: date | None = None
    expiration_date: date | None = None
    initial_quantity: int = 0
    current_quantity: int = 0          # Calculado desde movimientos
    notes: str | None = None
    created_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        if self.expiration_date is None:
            return False
        return date.today() > self.expiration_date

    @property
    def days_to_expiry(self) -> int | None:
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days
```

Tabla: `lots` (id, product_id FK, lot_number, manufacture_date, expiration_date, initial_quantity, current_quantity, notes, created_at)
Constraint UNIQUE: (product_id, lot_number)

### 5.2 Números de Serie (`src/inventory/serial/`)

```python
class SerialStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    RETURNED = "returned"
    SCRAPPED = "scrapped"

@dataclass
class SerialNumber(Entity):
    product_id: int
    serial_number: str
    status: SerialStatus = SerialStatus.AVAILABLE
    id: int | None = None
    lot_id: int | None = None          # Opcional: puede pertenecer a un lote
    location_id: int | None = None     # Ubicación actual
    purchase_order_id: int | None = None  # PO de entrada
    sale_id: int | None = None         # Venta de salida (Fase futura)
    created_at: datetime | None = None
    notes: str | None = None
```

Tabla: `serial_numbers` (id, product_id FK, serial_number UNIQUE, status, lot_id FK nullable, location_id FK nullable, purchase_order_id FK nullable, sale_id FK nullable, created_at)

### 5.3 Movimiento por Lote

Extender `Movement` para tracking por lote:
```python
@dataclass
class MovementLotItem(Entity):
    movement_id: int
    lot_id: int
    quantity: int
    id: int | None = None
```

Tabla: `movement_lot_items` (id, movement_id FK, lot_id FK, quantity)

### 5.4 Checklist Fase 5

- [x] Crear `src/inventory/lot/` completo (domain, app, infra)
- [x] Crear `src/inventory/serial/` completo (domain, app, infra)
- [x] Crear `MovementLotItem` entity/model/mapper/repository
- [x] Actualizar `PurchaseReceiptItem` para incluir `lot_number` y `serial_numbers`
- [x] Actualizar `PurchaseReceiptItemModel` con columnas `lot_number` (String) y `serial_numbers` (JSON)
- [x] Actualizar `ReceiveItemRequest` validator y `ReceiveItemInput` command con los nuevos campos
- [x] Event handler `handle_purchase_order_received_lots` → crear/actualizar lotes + `MovementLotItem`
- [x] Event handler `handle_purchase_order_received_serials` → crear seriales con lot_id resuelto
- [x] Commands: `CreateLotCommandHandler`, `UpdateLotCommandHandler`
- [x] Commands: `CreateSerialNumberCommandHandler`, `UpdateSerialStatusCommandHandler`
- [x] Queries: `GetLotsByProductQueryHandler`, `GetExpiringLotsQueryHandler`, `GetLotByIdQueryHandler`
- [x] Queries: `GetSerialsByProductQueryHandler`, `GetSerialByNumberQueryHandler`, `GetSerialByIdQueryHandler`
- [x] Especificaciones: `ExpiringLots(days)`, `ExpiredLots`, `LotsByProduct`
- [x] Rutas: `GET/POST /api/admin/lots`, `GET/PUT /api/admin/lots/{id}`
- [x] Rutas: `GET/POST /api/admin/serials`, `GET /api/admin/serials/{id}`, `PUT /api/admin/serials/{id}/status`
- [x] Registrar en `src/container.py` y `main.py`
- [x] Actualizar `config/base.py` con tags y tag group "Admin — Lots & Serials"
- [x] Actualizar `alembic/env.py` con `LotModel`, `MovementLotItemModel`, `SerialNumberModel`
- [x] Migración aplicada (`19e11200eb19`)
- [x] Tests: entidades (is_expired, days_to_expiry, mark_sold/reserved/returned/scrapped), especificaciones, commands, queries, event handlers (437 tests, 100% pass)

**Completada:** 2026-02-22

### Notas de implementación Fase 5

- **DI pattern crítico**: handlers SIEMPRE inyectan `Repository[T]` (la interfaz), NUNCA la clase concreta (`LotRepository`). Wireup registra repos con `as_type=Repository[E]` — si se inyecta la clase concreta falla al resolver.
- **Métodos del repo**: Usar `repo.first(product_id=..., lot_number=...)` en lugar de métodos custom en la clase concreta. El método `first(**kwargs)` filtra por keyword arguments y está disponible en la interfaz `Repository`.
- **`Specification` no es genérica**: `class LotsByProduct(Specification)` — NO `Specification[Lot]`. La clase base no soporta subscripción.
- **Event handlers**: usan `scope.get(Repository[Lot])`, `scope.get(Repository[MovementLotItem])`. Tests parchean `@patch("src.wireup_container")` (módulo raíz), no el módulo del handler.
- **`SerialStatus` usa `StrEnum`** — las transiciones inválidas lanzan `DomainError`. Transiciones válidas: AVAILABLE→SOLD, AVAILABLE→RESERVED, SOLD→RETURNED, cualquiera→SCRAPPED.
- **Lot event handler resuelve movement**: busca `Movement` por `reference_type="purchase_order"` y `reference_id=purchase_order_id` para crear `MovementLotItem` que vincula movimiento ↔ lote.
- **Serial event handler** resuelve `lot_id` buscando el lote por `(product_id, lot_number)` antes de crear el serial — permite vincular serial a lote en la misma recepción.

---

## FASE 6: Ajustes e Inventarios Físicos ✅ COMPLETADA (2026-02-23)

**Objetivo:** Permitir ajustes manuales de stock y conteos físicos (inventario cíclico).
**Módulo:** `src/inventory/adjustment/`
**Migración aplicada:** `c1ef129d19ad_create_inventory_adjustments_tables.py`

### 6.1 Ajuste de Inventario

```python
class AdjustmentStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class AdjustmentReason(StrEnum):
    PHYSICAL_COUNT = "physical_count"  # Conteo físico
    DAMAGED = "damaged"                # Mercancía dañada
    THEFT = "theft"                    # Robo/pérdida
    EXPIRATION = "expiration"          # Vencimiento
    SUPPLIER_ERROR = "supplier_error"  # Error de proveedor
    CORRECTION = "correction"          # Corrección manual
    OTHER = "other"

@dataclass
class InventoryAdjustment(Entity):
    warehouse_id: int
    reason: AdjustmentReason
    status: AdjustmentStatus = AdjustmentStatus.DRAFT
    id: int | None = None
    adjustment_date: datetime | None = None
    notes: str | None = None
    adjusted_by: str | None = None
    created_at: datetime | None = None

    def confirm(self) -> "InventoryAdjustment": ...
    def cancel(self) -> "InventoryAdjustment": ...

@dataclass
class AdjustmentItem(Entity):
    adjustment_id: int
    product_id: int
    location_id: int
    expected_quantity: int             # Cantidad en sistema
    actual_quantity: int               # Cantidad contada/real
    id: int | None = None
    lot_id: int | None = None
    notes: str | None = None

    @property
    def difference(self) -> int:
        return self.actual_quantity - self.expected_quantity
```

### 6.2 Flujo de confirmación

```
POST /api/admin/adjustments/{id}/confirm
    → ConfirmAdjustmentCommandHandler
        → Para cada AdjustmentItem donde difference != 0:
            → Si difference > 0: crear Movement IN (faltante en sistema)
            → Si difference < 0: crear Movement OUT (sobrante en sistema)
            → reference_type = "adjustment", reference_id = adjustment_id
        → Cambiar status a CONFIRMED
        → Publicar AdjustmentConfirmed event
```

### 6.3 Checklist Fase 6

- [x] Crear `src/inventory/adjustment/` completo
- [x] Entities: `InventoryAdjustment`, `AdjustmentItem`, `AdjustmentStatus`, `AdjustmentReason`
- [x] Commands: Create/Update/Delete/Confirm/Cancel Adjustment
- [x] Commands: AddAdjustmentItem, UpdateAdjustmentItem, RemoveAdjustmentItem
- [x] Queries: GetAllAdjustments, GetAdjustmentById, GetAdjustmentItems
- [x] Integración: al confirmar → crear Movements IN/OUT automáticamente, ítems con diff=0 se omiten
- [x] Especificación: `AdjustmentsByStatus`, `AdjustmentsByWarehouse`
- [x] Evento: `AdjustmentConfirmed` publicado al confirmar
- [x] AddAdjustmentItem auto-popula `expected_quantity` desde Stock actual
- [x] Rutas: `GET/POST /api/admin/adjustments`, `GET/PUT/DELETE /{id}`, `POST /{id}/confirm`, `POST /{id}/cancel`, `POST/GET /{id}/items`
- [x] Rutas: `PUT/DELETE /api/admin/adjustment-items/{id}`
- [x] Registrar en `src/container.py` y `main.py`
- [x] Actualizar `config/base.py` con tags y tag group "Admin — Adjustments"
- [x] Actualizar `alembic/env.py` con `InventoryAdjustmentModel`, `AdjustmentItemModel`
- [x] Migración aplicada (`c1ef129d19ad`) con `server_default` en `status` y `created_at`
- [x] Tests: 38 tests — entidades (8), commands (18), queries (6), especificaciones (6) — 480 total, 100% pass

**Completada:** 2026-02-23

### Notas de implementación Fase 6

- `ConfirmAdjustmentCommandHandler` inyecta `CreateMovementCommandHandler` directamente (no via event) — los movimientos se crean síncronamente en la misma transacción. El evento `MovementCreated` se propaga normalmente para actualizar Stock.
- `AddAdjustmentItemCommandHandler` usa `stock_repo.first(product_id=..., location_id=...)` para auto-poblar `expected_quantity`; si no hay stock registrado, usa 0.
- `AdjustmentItem.difference` es una `@property` calculada (actual - expected), no almacenada en BD. Se agrega al dict en queries y commands que lo devuelven.
- `cancel()` solo bloquea si status == CONFIRMED (no si es CANCELLED — idempotente en ese sentido).
- `server_default='draft'` en la migración para `status` y `server_default=sa.func.now()` para `created_at` — Alembic autogenerate no los agrega automáticamente.

---

## FASE 7: Transferencias entre Ubicaciones ✅ COMPLETADA (2026-02-23)

**Objetivo:** Mover stock entre ubicaciones o almacenes con trazabilidad.
**Módulo:** `src/inventory/transfer/`
**Migración aplicada:** `e1b2f1e9e74e_phase_7_stock_transfers_between_.py`

### 7.1 Orden de Transferencia

```python
class TransferStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"    # Stock reservado en origen
    RECEIVED = "received"      # Movimientos creados, stock movido
    CANCELLED = "cancelled"

@dataclass
class StockTransfer(Entity):
    source_location_id: int
    destination_location_id: int
    status: TransferStatus = TransferStatus.DRAFT
    id: int | None = None
    transfer_date: datetime | None = None
    requested_by: str | None = None
    notes: str | None = None
    created_at: datetime | None = None

    def confirm(self) -> "StockTransfer": ...   # DRAFT → CONFIRMED
    def receive(self) -> "StockTransfer": ...   # CONFIRMED → RECEIVED
    def cancel(self) -> "StockTransfer": ...    # DRAFT/CONFIRMED → CANCELLED

@dataclass
class StockTransferItem(Entity):
    transfer_id: int
    product_id: int
    quantity: int              # siempre positivo
    id: int | None = None
    lot_id: int | None = None
    notes: str | None = None
```

### 7.2 Flujo

```
POST /api/admin/transfers/{id}/confirm
    → ConfirmStockTransferCommandHandler
        → Valida source != destination (en Create)
        → Valida que haya ítems
        → Para cada ítem: verifica stock.available_quantity >= item.quantity
        → stock.reserved_quantity += item.quantity para cada ítem en origen
        → DRAFT → CONFIRMED
        → Publica StockTransferConfirmed

POST /api/admin/transfers/{id}/receive
    → ReceiveStockTransferCommandHandler
        → Para cada ítem:
            → stock.reserved_quantity -= item.quantity (liberar reserva)
            → crear Movement OUT en origen (reference_type="transfer")
            → crear Movement IN en destino (source_location_id=origen)
            → MovementCreated → StockEventHandler actualiza cantidades
        → CONFIRMED → RECEIVED
        → Publica StockTransferReceived

POST /api/admin/transfers/{id}/cancel
    → CancelStockTransferCommandHandler
        → Si era CONFIRMED: stock.reserved_quantity -= item.quantity por cada ítem
        → DRAFT/CONFIRMED → CANCELLED
        → Publica StockTransferCancelled(was_confirmed)
```

### 7.3 Checklist Fase 7

- [x] Crear `src/inventory/transfer/` completo
- [x] Entities: `StockTransfer`, `StockTransferItem`, `TransferStatus`
- [x] Events: `StockTransferConfirmed`, `StockTransferReceived`, `StockTransferCancelled`
- [x] Specifications: `TransfersByStatus`, `TransfersBySourceLocation`
- [x] Commands: Create/Update/Delete/Confirm/Receive/Cancel StockTransfer
- [x] Commands: AddTransferItem, UpdateTransferItem, RemoveTransferItem
- [x] Queries: GetAllTransfers (filtros: status, source_location_id), GetTransferById, GetTransferItems
- [x] Integración con `reserved_quantity` en Stock (Confirm reserva, Receive/Cancel libera)
- [x] Integración con `CreateMovementCommandHandler` (Receive crea OUT+IN síncronos)
- [x] Rutas: `GET/POST /api/admin/transfers`, `GET/PUT/DELETE /{id}`, `POST /{id}/confirm`, `POST /{id}/receive`, `POST /{id}/cancel`, `POST/GET /{id}/items`
- [x] Rutas: `PUT/DELETE /api/admin/transfer-items/{id}`
- [x] Registrar en `src/container.py` y `main.py`
- [x] Actualizar `config/base.py` con tags y tag group "Admin — Transfers"
- [x] Actualizar `alembic/env.py` con `StockTransferModel`, `StockTransferItemModel`
- [x] Migración aplicada (`e1b2f1e9e74e`)
- [x] Tests: 55 tests — entidades (11), commands (27), queries (9), especificaciones (8) — 535 total, 100% pass

**Completada:** 2026-02-23

### Notas de implementación Fase 7

- `ConfirmStockTransferCommandHandler` lanza `DomainError` si la transferencia no tiene ítems — evita confirmaciones vacías.
- La validación de `source != destination` ocurre en `CreateStockTransferCommandHandler`, no en la entidad — decisión de diseño para mantener la entidad simple.
- `ReceiveStockTransferCommandHandler` inyecta `CreateMovementCommandHandler` directamente (igual que Fase 6). Los movimientos OUT+IN se crean síncronamente; `MovementCreated` se propaga normalmente para actualizar Stock vía `StockEventHandler`.
- Al cancelar una transferencia CONFIRMED, se libera `reserved_quantity` antes de cambiar el estado — si el stock_repo no encuentra el stock (edge case), se omite sin error.
- `StockTransferCancelled` incluye `was_confirmed: bool` para que futuros event handlers sepan si había reservas que liberar (auditoría).
- No se implementó `IN_TRANSIT` — el ciclo DRAFT→CONFIRMED→RECEIVED es suficiente para transferencias intra-almacén; inter-almacén puede agregarse en una sub-fase futura.

---

## FASE 8: Alertas y Monitoreo de Stock

**Objetivo:** Notificar cuando stock está bajo mínimo o lotes próximos a vencer.
**Implementación:** Query handlers + endpoint de alertas (sin push notifications por ahora).

### 8.1 Tipos de alerta

```python
class AlertType(StrEnum):
    LOW_STOCK = "low_stock"           # quantity < min_stock
    OUT_OF_STOCK = "out_of_stock"     # quantity = 0
    EXPIRING_SOON = "expiring_soon"   # lot.days_to_expiry <= 30
    EXPIRED = "expired"               # lot.is_expired = True
    REORDER_POINT = "reorder_point"   # quantity <= reorder_point

@dataclass
class StockAlert:
    type: AlertType
    product_id: int
    product_name: str
    sku: str
    current_quantity: int
    threshold: int          # min_stock / reorder_point
    warehouse_id: int | None
    lot_id: int | None = None
    days_to_expiry: int | None = None
```

### 8.2 Queries de alertas

- `GetLowStockAlertsQuery` → productos donde quantity <= min_stock por warehouse
- `GetOutOfStockQuery` → productos donde quantity = 0
- `GetExpiringLotsQuery(days: int)` → lotes que vencen en N días
- `GetReorderPointAlertsQuery` → productos donde quantity <= reorder_point

### 8.3 Especificaciones

```python
class LowStockProducts(Specification[Stock]):
    def is_satisfied_by(self, candidate: Stock) -> bool:
        # Requiere el producto para saber min_stock
    def to_sql_criteria(self) -> list:
        # JOIN stocks con products WHERE stocks.quantity <= products.min_stock

class ExpiringLots(Specification[Lot]):
    def __init__(self, days: int = 30): ...
    def to_sql_criteria(self) -> list:
        # WHERE expiration_date <= TODAY + days AND current_quantity > 0
```

### 8.4 Checklist Fase 8

- [ ] Especificaciones: `LowStockProducts`, `ExpiringLots`, `OutOfStockProducts`
- [ ] Query handlers para alertas
- [ ] Rutas: `GET /api/admin/alerts/low-stock`, `/api/admin/alerts/expiring-lots`
- [ ] Tests: especificaciones de alertas

---

## FASE 9: Reportes y Valoración de Inventario

**Objetivo:** Reportes de valoración, rotación y movimientos para toma de decisiones.
**Módulo:** `src/reports/inventory/`

### 9.1 Reportes requeridos

#### Valoración de inventario (Average Cost)
```
GET /api/admin/reports/inventory/valuation?warehouse_id=&as_of_date=

Response:
{
  "total_value": Decimal,
  "as_of_date": date,
  "items": [
    {
      "product_id": int,
      "product_name": str,
      "sku": str,
      "quantity": int,
      "average_cost": Decimal,
      "total_value": Decimal
    }
  ]
}
```

**Cálculo average cost:** `SUM(movement.quantity * purchase_price) / SUM(movement.quantity)` para movimientos IN

#### Rotación de productos
```
GET /api/admin/reports/inventory/rotation?from_date=&to_date=&warehouse_id=

Response por producto:
{
  "product_id": int,
  "total_in": int,
  "total_out": int,
  "turnover_rate": Decimal,  # out / average_stock
  "days_of_stock": int       # current_stock / (out / days_in_period)
}
```

#### Historial de movimientos
```
GET /api/admin/reports/inventory/movements?product_id=&from_date=&to_date=&type=&warehouse_id=

Response paginado con filtros
```

#### Resumen por almacén
```
GET /api/admin/reports/inventory/summary?warehouse_id=

Response: total productos, total SKUs, valor total, alertas activas
```

### 9.2 Implementación

- Son principalmente **Query handlers** que ejecutan SQL agregado
- Pueden usar queries directas a la sesión (sin pasar por Repository genérico)
- No requieren dominio complejo, principalmente lógica de consulta

### 9.3 Checklist Fase 9

- [ ] Crear `src/reports/inventory/` con query handlers para cada reporte
- [ ] Queries: ValuationReport, RotationReport, MovementHistoryReport, WarehouseSummaryReport
- [ ] Paginación en MovementHistoryReport
- [ ] Filtros: by product, by warehouse, by date range, by type
- [ ] Rutas: `/api/admin/reports/inventory/...`
- [ ] Tests: correctness de cálculos de valoración

---

## FASE 10: Integración con POS/Ventas (Futura)

> **NOTA:** Esta fase se desarrolla DESPUÉS de que el módulo de ventas/POS esté completo.

### Puntos de integración requeridos

1. **Stock Check en Venta**: antes de confirmar venta, verificar disponibilidad (multi-ubicación)
2. **Reservas**: al crear venta CONFIRMED, reservar stock (`reserved_quantity`)
3. **Liberación**: al cancelar venta, liberar reserva
4. **Salida definitiva**: al INVOICED, reducir stock real
5. **Seriales**: asignar serial_number específico a SaleItem
6. **Lotes**: registrar qué lote sale (FEFO: First Expired, First Out)

---

## Resumen de Fases y Dependencias

```
Phase 1: Catálogo (UoM + Product mejorado)
    ↓
Phase 2: Almacenes & Ubicaciones (refactorizar Stock)
    ↓
Phase 3: Proveedores
    ↓
Phase 4: Órdenes de Compra (depende: Suppliers + Warehouses + Inventory mejorado)
    ↓
Phase 5: Lotes & Seriales (depende: Purchase Orders para recepción)
    ↓
Phase 6: Ajustes (depende: Stock multi-ubicación)
Phase 7: Transferencias (depende: Stock multi-ubicación)
    ↓
Phase 8: Alertas (depende: Products con min_stock + Lots)
    ↓
Phase 9: Reportes (depende: todo lo anterior)
    ↓
Phase 10: Integración POS (futura, depende: Seriales + Lotes + Reservas)
```

---

## Migraciones Planeadas

| Fase | Migración | Operación |
|------|-----------|-----------|
| 1 | `create_units_of_measure` | Nueva tabla + FK en products |
| 1 | `enhance_products` | Nuevas columnas en products |
| 2 | `create_warehouses_and_locations` | Nuevas tablas |
| 2 | `refactor_stock_to_location_id` | stocks: location(str) → location_id(FK) |
| 2 | `add_stock_reserved_quantity` | Nueva columna en stocks |
| 2 | `enhance_movements` | Nuevas columnas en movements |
| 3 | `create_suppliers` | Nuevas tablas |
| 4 | `create_purchase_orders` | Nuevas tablas |
| 5 | `create_lots_and_serials` | Nuevas tablas |
| 6 | `c1ef129d19ad_create_inventory_adjustments_tables` | Nuevas tablas |
| 7 | `e1b2f1e9e74e_phase_7_stock_transfers_between_` | Nuevas tablas |

---

## Contexto Técnico para Claude (referencia entre sesiones)

### Cómo registrar un nuevo módulo

```python
# 1. En src/nuevo_modulo/infra/container.py:
from wireup import DependencyContainer
from .repositories import NuevoRepository
from .mappers import NuevoMapper
from ..app.commands.create import CreateNuevoCommandHandler
from ..app.queries.get_all import GetAllNuevoQueryHandler

NUEVO_INJECTABLES = [
    NuevoMapper,
    NuevoRepository,
    CreateNuevoCommandHandler,
    GetAllNuevoQueryHandler,
]

# 2. En src/container.py, agregar:
from src.nuevo_modulo.infra.container import NUEVO_INJECTABLES
# ... en create_wireup_container():
container.register_all(NUEVO_INJECTABLES)
# Si tiene event handlers:
import src.nuevo_modulo.infra.event_handlers  # noqa

# 3. En main.py, agregar:
from src.nuevo_modulo.infra.routes import NuevoRouter
app.include_router(NuevoRouter, prefix="/api/admin/nuevo-modulo", tags=["Nuevo Módulo"])
```

### Template de Command Handler

```python
from dataclasses import dataclass
from wireup import injectable
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.app.events import EventPublisher
from ..domain.entities import MiEntidad
from ..app.types import MiEntidadOutput

@dataclass
class CreateMiEntidadCommand(Command):
    name: str
    # ... otros campos

@injectable(lifetime="scoped")
class CreateMiEntidadCommandHandler(CommandHandler[CreateMiEntidadCommand, MiEntidadOutput]):
    def __init__(
        self,
        repository: Repository[MiEntidad],
        publisher: EventPublisher,
    ):
        self.repository = repository
        self.publisher = publisher

    def _handle(self, command: CreateMiEntidadCommand) -> MiEntidadOutput:
        entity = MiEntidad(name=command.name)
        saved = self.repository.create(entity)
        # self.publisher.publish(MiEntidadCreated(aggregate_id=saved.id, ...))
        return MiEntidadOutput(id=saved.id, name=saved.name)
```

### Template de Repository

```python
from wireup import injectable
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import SqlAlchemyRepository
from ..domain.entities import MiEntidad
from .models import MiEntidadModel

@injectable(lifetime="scoped", as_type=Repository[MiEntidad])
class MiEntidadRepository(SqlAlchemyRepository[MiEntidad]):
    __model__ = MiEntidadModel
```

### Template de Mapper

```python
from wireup import injectable
from src.shared.infra.mappers import Mapper
from ..domain.entities import MiEntidad
from .models import MiEntidadModel

@injectable
class MiEntidadMapper(Mapper[MiEntidad, MiEntidadModel]):
    __entity__ = MiEntidad
    __exclude_fields__ = frozenset({"created_at"})  # Campos auto-generados
```

### Template de Route con wireup

```python
from fastapi import APIRouter
from wireup.integration.fastapi import Inject
from ..app.commands.create import CreateMiEntidadCommand, CreateMiEntidadCommandHandler
from .validators import MiEntidadRequest, MiEntidadResponse

MiEntidadRouter = APIRouter()

@MiEntidadRouter.post("/", response_model=MiEntidadResponse)
def create(
    body: MiEntidadRequest,
    handler: Annotated[CreateMiEntidadCommandHandler, Inject()],
):
    command = CreateMiEntidadCommand(name=body.name)
    result = handler.handle(command)
    return MiEntidadResponse(**result)
```

### Validators (Pydantic con aliases camelCase)

```python
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

class MiEntidadRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str
    some_field: str | None = None    # → someField en JSON

class MiEntidadResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    id: int
    name: str
    some_field: str | None = None
```

---

*Última actualización: 2026-02-23*
*Próxima fase a desarrollar: FASE 8 — Alertas y Monitoreo de Stock*
