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

## FASE 2: Almacenes y Ubicaciones

**Objetivo:** Soporte multi-almacén con ubicaciones físicas dentro de cada almacén.
**Impacto en BD:** Nuevas tablas `warehouses`, `locations`. Stock pasa a ser por ubicación.

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

- [ ] Crear `src/inventory/warehouse/` completo
- [ ] Crear `src/inventory/location/` completo
- [ ] Refactorizar `Stock` entity → `location_id` (reemplaza `location: str`)
- [ ] Agregar `location_id`, `source_location_id`, `reference_type`, `reference_id` a `Movement`
- [ ] Actualizar event handler `MovementCreated` → usa location_id para actualizar Stock
- [ ] Actualizar `StockModel` (migration: rename location → location_id, add reserved_quantity)
- [ ] Agregar `MovementModel` columnas nuevas
- [ ] Handlers: CRUD warehouses, CRUD locations, GetStock (filtrado por warehouse/location/product)
- [ ] Rutas: `/api/admin/warehouses`, `/api/admin/locations`, `/api/admin/stock`
- [ ] Registrar en container y main.py
- [ ] Migración y aplicar
- [ ] Tests: warehouse CRUD, location CRUD, stock multi-ubicación

---

## FASE 3: Gestión de Proveedores

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

- [ ] Crear `src/suppliers/` con estructura completa
- [ ] Entities: `Supplier`, `SupplierContact`, `SupplierProduct`
- [ ] Models: `SupplierModel`, `SupplierContactModel`, `SupplierProductModel`
- [ ] Commands: Create/Update/Delete/Activate/Deactivate Supplier
- [ ] Commands: Create/Update/Delete SupplierContact
- [ ] Commands: Create/Update/Delete SupplierProduct (catálogo de compra)
- [ ] Queries: GetAll/GetById Supplier, GetContacts, GetSupplierProducts, GetProductSuppliers
- [ ] Rutas: `/api/admin/suppliers`, `/api/admin/suppliers/{id}/contacts`, `/api/admin/suppliers/{id}/products`
- [ ] Eventos: SupplierCreated, SupplierActivated, SupplierDeactivated
- [ ] Migración y aplicar
- [ ] Tests: CRUD supplier, contactos, catálogo de compra

---

## FASE 4: Órdenes de Compra

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

- [ ] Crear `src/purchasing/` con estructura completa
- [ ] Entities: `PurchaseOrder`, `PurchaseOrderItem`, `PurchaseReceipt`, `PurchaseReceiptItem`
- [ ] Models + Mappers + Repositories
- [ ] Commands: CreatePO, UpdatePO, DeletePO (solo DRAFT), SendPO, CancelPO
- [ ] Commands: AddPOItem, UpdatePOItem, RemovePOItem
- [ ] Commands: CreatePurchaseReceipt (recepción con items, puede ser parcial)
- [ ] Queries: GetAllPOs, GetPOById, GetPOItems, GetPOReceipts
- [ ] Eventos y event handlers (PurchaseOrderReceived → crea Movements)
- [ ] Generación automática de order_number (PO-YYYY-NNNN)
- [ ] Rutas: `/api/admin/purchase-orders`, `/api/admin/purchase-orders/{id}/items`, `/api/admin/purchase-orders/{id}/receive`
- [ ] Migración y aplicar
- [ ] Tests: ciclo completo PO, recepción parcial, integración con stock

---

## FASE 5: Lotes y Números de Serie

**Objetivo:** Trazabilidad completa de mercancía por lote (farmacia, alimentos) o serial (electrónicos).
**Módulo:** Extender `src/inventory/`

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

- [ ] Crear `src/inventory/lot/` completo
- [ ] Crear `src/inventory/serial/` completo
- [ ] Crear `MovementLotItem` entity/model
- [ ] Actualizar `PurchaseReceiptItem` para incluir lot_number/serial_numbers
- [ ] Actualizar event handler de PurchaseOrderReceived → crear/actualizar lotes
- [ ] Commands: CreateLot, UpdateLot (quantity manual), CreateSerialNumber, UpdateSerialStatus
- [ ] Queries: GetLotsByProduct, GetExpiringLots (próximos N días), GetSerialByNumber, GetSerialsByProduct
- [ ] Especificaciones: `ExpiringLots(days: int)`, `ActiveSerials`, `SerialsByStatus`
- [ ] Rutas: `/api/admin/lots`, `/api/admin/serials`
- [ ] Tests: control de lotes, expiración, seriales

---

## FASE 6: Ajustes e Inventarios Físicos

**Objetivo:** Permitir ajustes manuales de stock y conteos físicos (inventario cíclico).
**Módulo:** `src/inventory/adjustment/`

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

- [ ] Crear `src/inventory/adjustment/` completo
- [ ] Entities: `InventoryAdjustment`, `AdjustmentItem`
- [ ] Commands: Create/Update/Delete/Confirm/Cancel Adjustment
- [ ] Commands: AddAdjustmentItem, UpdateAdjustmentItem, RemoveAdjustmentItem
- [ ] Queries: GetAllAdjustments, GetAdjustmentById, GetAdjustmentItems
- [ ] Integración: al confirmar → crear Movements automáticamente
- [ ] Especificación: `AdjustmentsByStatus`, `AdjustmentsByWarehouse`
- [ ] Rutas: `/api/admin/adjustments`
- [ ] Tests: ciclo completo, diferencias positivas/negativas

---

## FASE 7: Transferencias entre Ubicaciones

**Objetivo:** Mover stock entre ubicaciones o almacenes con trazabilidad.
**Módulo:** `src/inventory/transfer/`

### 7.1 Orden de Transferencia

```python
class TransferStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"    # Stock reservado en origen
    IN_TRANSIT = "in_transit"  # En movimiento (para inter-almacén)
    RECEIVED = "received"      # Recibido en destino
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

@dataclass
class StockTransferItem(Entity):
    transfer_id: int
    product_id: int
    quantity: int
    id: int | None = None
    lot_id: int | None = None
```

### 7.2 Flujo

```
Confirmar → reservar stock en origen (reserved_quantity += qty)
Recibir  → crear Movement OUT origen + Movement IN destino
           → liberar reserva en origen
           → actualizar stock en destino
```

### 7.3 Checklist Fase 7

- [ ] Crear `src/inventory/transfer/` completo
- [ ] Entities + Models + Handlers
- [ ] Integración con `reserved_quantity` en Stock
- [ ] Rutas: `/api/admin/transfers`
- [ ] Tests: transferencia simple, inter-almacén

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
| 6 | `create_adjustments` | Nuevas tablas |
| 7 | `create_transfers` | Nuevas tablas |

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

*Última actualización: 2026-02-22*
*Próxima fase a desarrollar: FASE 2 — Almacenes y Ubicaciones*
