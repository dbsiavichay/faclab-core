# Roadmap: Evolución a Sistema Completo de Ventas e Inventario

## 🎯 Visión General

Convertir el proyecto actual (Warehouse API) en el **core** de un sistema completo de ventas e inventario, expandiendo la funcionalidad de gestión básica a un sistema empresarial integrado.

---

## 📦 Estructura de Proyecto Propuesta

### Arquitectura de Monorepo Modular

```
sales-system/
├── core/                           # Módulo core (actual warehouse)
│   ├── src/
│   │   ├── shared/                # Compartido entre módulos
│   │   │   ├── domain/           # Entidades base, value objects
│   │   │   ├── app/              # Interfaces base (Repository, UseCase)
│   │   │   └── infra/            # DI, DB, middleware, utilities
│   │   ├── inventory/            # Gestión de inventario (stock + movements)
│   │   │   ├── domain/
│   │   │   ├── app/
│   │   │   └── infra/
│   │   ├── catalog/              # Productos y categorías
│   │   │   ├── domain/
│   │   │   ├── app/
│   │   │   └── infra/
│   │   ├── sales/                # NUEVO: Ventas
│   │   ├── customers/            # NUEVO: Clientes
│   │   ├── suppliers/            # NUEVO: Proveedores
│   │   ├── purchases/            # NUEVO: Compras
│   │   ├── pricing/              # NUEVO: Precios y promociones
│   │   ├── warehouse/            # NUEVO: Múltiples almacenes
│   │   └── reporting/            # NUEVO: Reportes
│   ├── alembic/
│   ├── config/
│   ├── main.py
│   └── requirements.txt
├── tests/                         # Tests del core
├── docs/                          # Documentación
└── docker-compose.yml
```

### Razón de la Separación

**Catalog vs Inventory:**
- **Catalog**: Información de productos (relativamente estática)
- **Inventory**: Movimiento y stock (transaccional)
- Facilita permisos y escalabilidad futura

---

## 📋 Módulos de Negocio

### Prioridad 1: Fundación (2-3 semanas)

#### 1. Refactorizar Estructura Actual

**Cambios:**
```
product + category → catalog/
stock + movement → inventory/
core/domain + core/app + core/infra → shared/
```

#### 2. Módulo Customers (Clientes)

**Entidades de Dominio:**
```python
Customer {
    id: int
    code: str                    # Código único del cliente
    name: str
    tax_id: str                 # RUC/NIT/Tax ID
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    customer_type: CustomerType  # RETAIL, WHOLESALE
    credit_limit: Decimal
    payment_terms: int          # Días de crédito
    is_active: bool
    created_at: datetime
}

CustomerContact {
    id: int
    customer_id: int
    name: str
    role: str
    email: str
    phone: str
}
```

**Casos de Uso:**
- Crear/actualizar/eliminar cliente
- Buscar clientes (por código, nombre, tax_id)
- Obtener historial de compras del cliente
- Gestionar límite de crédito
- Activar/desactivar cliente

**Endpoints:**
```
POST   /customers
GET    /customers
GET    /customers/{id}
PUT    /customers/{id}
DELETE /customers/{id}
GET    /customers/{id}/sales-history
POST   /customers/{id}/contacts
```

#### 3. Módulo Sales (Ventas)

**Entidades de Dominio:**
```python
Sale {
    id: int
    code: str                    # Número de venta (auto-generado)
    customer_id: int
    sale_date: datetime
    status: SaleStatus          # DRAFT, CONFIRMED, INVOICED, CANCELLED
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    payment_status: PaymentStatus  # PENDING, PARTIAL, PAID
    notes: str
    created_by: str
    created_at: datetime
}

SaleItem {
    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    subtotal: Decimal
}

Payment {
    id: int
    sale_id: int
    payment_date: datetime
    amount: Decimal
    payment_method: PaymentMethod  # CASH, CARD, TRANSFER, CREDIT
    reference: str
    notes: str
}
```

**Casos de Uso Clave:**
- `CreateSaleUseCase`: Crear venta en estado DRAFT
- `AddSaleItemUseCase`: Agregar items a la venta
- `RemoveSaleItemUseCase`: Quitar items
- `CalculateSaleTotalsUseCase`: Calcular subtotal, impuestos, descuentos
- `ConfirmSaleUseCase`: Confirmar venta → **Genera Movement(OUT) automáticamente**
- `RegisterPaymentUseCase`: Registrar pagos
- `CancelSaleUseCase`: Anular venta → **Revierte movimiento de inventario**
- `GetSalesByCustomerUseCase`: Historial de ventas por cliente
- `GetSalesByDateRangeUseCase`: Ventas por periodo

**Endpoints:**
```
POST   /sales                    # Crear venta (DRAFT)
GET    /sales
GET    /sales/{id}
PUT    /sales/{id}
POST   /sales/{id}/items         # Agregar item
DELETE /sales/{id}/items/{item_id}
POST   /sales/{id}/confirm       # Confirmar → genera movimiento
POST   /sales/{id}/cancel        # Anular
POST   /sales/{id}/payments      # Registrar pago
GET    /sales/{id}/payments
```

**Reglas de Negocio:**
- Al confirmar venta, validar stock disponible
- Si stock insuficiente, no permitir confirmación
- Al confirmar, crear Movement(type=OUT) por cada item
- Al anular, crear Movement(type=IN) para revertir
- Solo se pueden anular ventas CONFIRMED (no INVOICED)
- Payment total no puede exceder sale total

---

### Prioridad 2: Operaciones (2-3 semanas)

#### 4. Módulo Suppliers (Proveedores)

**Entidades de Dominio:**
```python
Supplier {
    id: int
    code: str
    name: str
    tax_id: str
    email: str
    phone: str
    address: str
    payment_terms: int          # Días para pago
    lead_time_days: int         # Tiempo de entrega
    is_active: bool
}

SupplierProduct {
    id: int
    supplier_id: int
    product_id: int
    supplier_sku: str           # SKU del proveedor
    cost_price: Decimal
    min_order_qty: int
}
```

**Casos de Uso:**
- CRUD de proveedores
- Asociar productos con proveedores
- Obtener mejores precios por producto
- Listar productos de un proveedor

**Endpoints:**
```
POST   /suppliers
GET    /suppliers
GET    /suppliers/{id}
PUT    /suppliers/{id}
DELETE /suppliers/{id}
POST   /suppliers/{id}/products
GET    /suppliers/{id}/products
```

#### 5. Módulo Purchases (Compras/Adquisiciones)

**Entidades de Dominio:**
```python
PurchaseOrder {
    id: int
    code: str
    supplier_id: int
    order_date: datetime
    expected_date: datetime
    status: POStatus            # DRAFT, SENT, RECEIVED, CANCELLED
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    notes: str
}

PurchaseOrderItem {
    id: int
    purchase_order_id: int
    product_id: int
    quantity: int
    unit_cost: Decimal
    subtotal: Decimal
    received_quantity: int      # Cantidad recibida
}

PurchaseReceipt {
    id: int
    purchase_order_id: int
    receipt_date: datetime
    received_by: str
    notes: str
}
```

**Casos de Uso Clave:**
- `CreatePurchaseOrderUseCase`: Crear orden de compra
- `AddPurchaseItemUseCase`: Agregar items
- `SendPurchaseOrderUseCase`: Enviar a proveedor (SENT)
- `ReceivePurchaseUseCase`: Recibir mercancía → **Genera Movement(IN)**
- `PartialReceivePurchaseUseCase`: Recepción parcial
- `CancelPurchaseOrderUseCase`: Cancelar orden

**Endpoints:**
```
POST   /purchases
GET    /purchases
GET    /purchases/{id}
PUT    /purchases/{id}
POST   /purchases/{id}/items
POST   /purchases/{id}/send
POST   /purchases/{id}/receive   # Genera movimiento IN
POST   /purchases/{id}/cancel
```

**Reglas de Negocio:**
- Solo órdenes en SENT pueden recibirse
- Al recibir, crear Movement(type=IN) por cada item
- Permitir recepción parcial (received_qty < ordered_qty)
- Actualizar estado a RECEIVED cuando todos los items estén completos

---

### Prioridad 3: Inteligencia de Negocio (1-2 semanas)

#### 6. Módulo Pricing (Precios)

**Entidades de Dominio:**
```python
PriceList {
    id: int
    name: str
    currency: str
    is_default: bool
    valid_from: datetime
    valid_to: datetime
}

ProductPrice {
    id: int
    price_list_id: int
    product_id: int
    base_price: Decimal
    discount_percent: Decimal
    min_quantity: int           # Precio por volumen
    customer_type: CustomerType # RETAIL, WHOLESALE
}

Promotion {
    id: int
    name: str
    promotion_type: PromotionType  # DISCOUNT, BUNDLE, BUY_X_GET_Y
    value: Decimal
    valid_from: datetime
    valid_to: datetime
    applicable_to: str          # PRODUCTS, CATEGORIES, ALL
    product_ids: List[int]
    category_ids: List[int]
}
```

**Casos de Uso:**
- `GetProductPriceUseCase`: Obtener precio según lista, cliente, cantidad
- `ApplyPromotionsUseCase`: Aplicar promociones activas
- `CalculateDiscountUseCase`: Calcular descuentos por volumen
- `CreatePriceListUseCase`: Gestionar listas de precios

**Integración con Sales:**
- Al agregar SaleItem, obtener precio desde pricing module
- Aplicar promociones automáticamente
- Calcular descuentos por volumen

#### 7. Módulo Warehouse (Multi-almacén)

**Entidades de Dominio:**
```python
Warehouse {
    id: int
    code: str
    name: str
    address: str
    is_main: bool
    is_active: bool
}

# Modificar Stock actual:
Stock {
    id: int
    product_id: int
    warehouse_id: int           # NUEVO
    location: str               # Pasillo/rack/nivel
    quantity: int
    min_stock: int
    max_stock: int
}

# Modificar Movement actual:
Movement {
    id: int
    product_id: int
    warehouse_id: int           # NUEVO
    type: MovementType
    quantity: int
    date: datetime
    reference_type: str         # SALE, PURCHASE, ADJUSTMENT, TRANSFER
    reference_id: int
    notes: str
}

# Nueva entidad:
StockTransfer {
    id: int
    from_warehouse_id: int
    to_warehouse_id: int
    transfer_date: datetime
    status: TransferStatus      # PENDING, IN_TRANSIT, RECEIVED
    notes: str
}

StockTransferItem {
    id: int
    transfer_id: int
    product_id: int
    quantity: int
}
```

**Casos de Uso:**
- `CreateStockTransferUseCase`: Transferencia entre almacenes
- `ConfirmTransferUseCase`: Confirmar envío → Movement(OUT) en origen
- `ReceiveTransferUseCase`: Recibir en destino → Movement(IN)
- `GetStockByWarehouseUseCase`: Stock por almacén
- `GetLowStockByWarehouseUseCase`: Alertas por ubicación

**Endpoints:**
```
POST   /warehouses
GET    /warehouses
GET    /warehouses/{id}/stock
POST   /stock-transfers
POST   /stock-transfers/{id}/confirm
POST   /stock-transfers/{id}/receive
```

---

### Prioridad 4: Análisis (1 semana)

#### 8. Módulo Reporting (Reportes)

**No necesita entidades propias, usa queries agregadas**

**Reportes Implementados:**

**Ventas:**
- Ventas por periodo (día, semana, mes, año)
- Productos más vendidos
- Clientes top (por volumen y valor)
- Margen de ganancia por producto
- Análisis de descuentos aplicados
- Ventas por vendedor (futuro)

**Inventario:**
- Stock valorizado (por warehouse)
- Productos con stock bajo
- Productos sin movimiento (X días)
- Rotación de inventario (inventory turnover)
- Análisis ABC de productos

**Compras:**
- Compras por proveedor
- Análisis de costos
- Tiempo de entrega promedio por proveedor

**Financiero:**
- Aging de cuentas por cobrar
- Ventas vs cobros (cash flow)
- Análisis de métodos de pago

**Endpoints:**
```
GET /reports/sales/by-period?from=2024-01-01&to=2024-12-31
GET /reports/sales/top-products?limit=10
GET /reports/sales/top-customers?limit=10
GET /reports/inventory/stock-value
GET /reports/inventory/low-stock
GET /reports/inventory/turnover
GET /reports/purchases/by-supplier
GET /reports/financial/accounts-receivable
```

---

## 🔄 Flujos de Negocio Integrados

### Flujo de Venta Completo

```
1. Cliente solicita productos
   ↓
2. POST /sales → Crear Sale (status=DRAFT)
   ↓
3. POST /sales/{id}/items → Agregar SaleItems
   ├─> Obtener precio desde Pricing module
   ├─> Aplicar promociones activas
   └─> Verificar stock disponible (warning, no bloqueante)
   ↓
4. Sistema calcula totales
   ├─> subtotal = sum(item.subtotal)
   ├─> tax = subtotal * tax_rate
   ├─> total = subtotal + tax - discount
   ↓
5. POST /sales/{id}/confirm → Confirmar venta
   ├─> Validar stock disponible (bloqueante)
   ├─> Si stock insuficiente → error 400
   ├─> Cambiar status a CONFIRMED
   └─> Generar Movement(type=OUT) por cada item
       ├─> reference_type = "SALE"
       └─> reference_id = sale.id
   ↓
6. Sistema actualiza Stock
   └─> stock.quantity -= sale_item.quantity
   ↓
7. POST /sales/{id}/payments → Registrar pagos
   ├─> Validar amount <= sale.total
   ├─> payment_total = sum(payments.amount)
   └─> Si payment_total == sale.total → payment_status = PAID
   ↓
8. Generar factura (futuro: invoicing module)
```

### Flujo de Compra Completo

```
1. Sistema detecta stock bajo (stock.quantity <= min_stock)
   ↓
2. POST /purchases → Crear PurchaseOrder (status=DRAFT)
   ├─> Seleccionar supplier (mejor precio o proveedor preferido)
   └─> supplier_id = best_supplier.id
   ↓
3. POST /purchases/{id}/items → Agregar items
   ├─> product_id
   ├─> quantity = max_stock - current_stock
   └─> unit_cost = supplier_product.cost_price
   ↓
4. POST /purchases/{id}/send → Enviar a proveedor
   └─> status = SENT
   ↓
5. Proveedor entrega mercancía
   ↓
6. POST /purchases/{id}/receive → Registrar recepción
   ├─> Crear PurchaseReceipt
   ├─> Actualizar received_quantity en items
   └─> Generar Movement(type=IN) por cada item
       ├─> reference_type = "PURCHASE"
       └─> reference_id = purchase_order.id
   ↓
7. Sistema actualiza Stock
   └─> stock.quantity += received_quantity
   ↓
8. Si todos los items recibidos completos
   └─> status = RECEIVED
```

### Flujo de Transferencia entre Almacenes

```
1. POST /stock-transfers → Crear transferencia
   ├─> from_warehouse_id
   ├─> to_warehouse_id
   └─> items: [{product_id, quantity}]
   ↓
2. POST /stock-transfers/{id}/confirm → Confirmar envío
   ├─> Validar stock en almacén origen
   ├─> status = IN_TRANSIT
   └─> Generar Movement(type=OUT, warehouse=origen)
       ├─> reference_type = "TRANSFER"
       └─> reference_id = transfer.id
   ↓
3. Stock origen se reduce
   └─> stock.quantity -= quantity (where warehouse_id = origen)
   ↓
4. POST /stock-transfers/{id}/receive → Recibir en destino
   ├─> status = RECEIVED
   └─> Generar Movement(type=IN, warehouse=destino)
   ↓
5. Stock destino aumenta
   └─> stock.quantity += quantity (where warehouse_id = destino)
```

---

## 🏗️ Plan de Implementación

### Fase 0: Bugs Críticos (1 día) ✅

**Tareas:**
1. ✅ Renombrar `__ini__.py` → `__init__.py` (2 archivos)
2. ✅ Crear `src/core/domain/ports.py` con interfaz Logger
3. ✅ Corregir types.py (product_id: int)
4. ✅ Agregar `self` a métodos abstractos de Mapper

### Fase 1: Preparación (Semana 1)

**Tareas:**
- [ ] Refactorizar estructura de carpetas:
  ```
  src/product → src/catalog/product
  src/category → src/catalog/category (merge con product)
  src/stock → src/inventory/stock
  src/movement → src/inventory/movement
  src/core → src/shared
  ```
- [ ] Actualizar imports en todos los archivos
- [ ] Mover domain/app/infra comunes a shared/
- [ ] Mejorar BaseRepository (fix filter return type)
- [ ] Implementar paginación funcional en todos los endpoints
- [ ] Crear tests básicos (repository + use cases)
- [ ] Actualizar README.md con estructura nueva
- [ ] Crear migration para renombrar tablas si es necesario

**Entregables:**
- Estructura modular clara
- Tests pasando
- Documentación actualizada

### Fase 2: Clientes y Ventas Básicas (Semanas 2-3)

**Semana 2: Módulo Customers**
- [ ] Crear estructura customers/ (domain, app, infra)
- [ ] Implementar entidades Customer y CustomerContact
- [ ] Crear modelos SQLAlchemy
- [ ] Implementar repository y mapper
- [ ] Crear use cases (CRUD + búsqueda)
- [ ] Crear controller y routes
- [ ] Registrar en DI container
- [ ] Migration para tablas customers
- [ ] Tests unitarios (>80% coverage)
- [ ] Tests de integración (API endpoints)

**Semana 3: Módulo Sales**
- [ ] Crear estructura sales/ (domain, app, infra)
- [ ] Implementar entidades Sale, SaleItem, Payment
- [ ] Crear modelos SQLAlchemy con relaciones
- [ ] Implementar repositories y mappers
- [ ] Crear use cases:
  - [ ] CreateSaleUseCase (DRAFT)
  - [ ] AddSaleItemUseCase (validar stock disponible)
  - [ ] CalculateSaleTotalsUseCase
  - [ ] ConfirmSaleUseCase (→ generar movements)
  - [ ] RegisterPaymentUseCase
  - [ ] CancelSaleUseCase (→ revertir movements)
- [ ] Integración con inventory module
- [ ] Controller y routes
- [ ] Migration para tablas sales
- [ ] Tests de integración sales ↔ inventory

**Entregables:**
- Módulo customers completo y funcional
- Módulo sales integrado con inventory
- Stock se actualiza automáticamente al confirmar/anular ventas
- Tests de integración pasando

### Fase 3: Proveedores y Compras (Semanas 4-5)

**Semana 4: Módulo Suppliers**
- [ ] Crear estructura suppliers/ (domain, app, infra)
- [ ] Implementar entidades Supplier y SupplierProduct
- [ ] Crear modelos SQLAlchemy
- [ ] Implementar repositories y mappers
- [ ] Use cases (CRUD + asociar productos)
- [ ] Controller y routes
- [ ] Migration
- [ ] Tests

**Semana 5: Módulo Purchases**
- [ ] Crear estructura purchases/ (domain, app, infra)
- [ ] Implementar entidades PurchaseOrder, PurchaseOrderItem, PurchaseReceipt
- [ ] Crear modelos SQLAlchemy
- [ ] Implementar repositories y mappers
- [ ] Use cases:
  - [ ] CreatePurchaseOrderUseCase
  - [ ] AddPurchaseItemUseCase
  - [ ] SendPurchaseOrderUseCase
  - [ ] ReceivePurchaseUseCase (→ generar movements IN)
  - [ ] PartialReceivePurchaseUseCase
- [ ] Integración con inventory y suppliers
- [ ] Controller y routes
- [ ] Migration
- [ ] Tests de integración purchases ↔ inventory

**Entregables:**
- Módulo suppliers completo
- Módulo purchases integrado
- Stock se actualiza al recibir compras
- Flujo completo de reabastecimiento funcionando

### Fase 4: Precios y Multi-almacén (Semanas 6-7)

**Semana 6: Módulo Pricing**
- [ ] Crear estructura pricing/ (domain, app, infra)
- [ ] Implementar entidades PriceList, ProductPrice, Promotion
- [ ] Modelos SQLAlchemy
- [ ] Repositories y mappers
- [ ] Use cases:
  - [ ] GetProductPriceUseCase (por lista, cliente, cantidad)
  - [ ] ApplyPromotionsUseCase
  - [ ] CalculateDiscountUseCase
  - [ ] CRUD de listas de precios
- [ ] Integrar con sales module
- [ ] Modificar AddSaleItemUseCase para usar pricing
- [ ] Migration
- [ ] Tests

**Semana 7: Multi-warehouse**
- [ ] Crear estructura warehouse/ (domain, app, infra)
- [ ] Implementar entidad Warehouse
- [ ] Modificar Stock para incluir warehouse_id
- [ ] Modificar Movement para incluir warehouse_id
- [ ] Implementar StockTransfer y StockTransferItem
- [ ] Migration para agregar warehouse_id (con default warehouse)
- [ ] Use cases:
  - [ ] CreateStockTransferUseCase
  - [ ] ConfirmTransferUseCase (→ Movement OUT)
  - [ ] ReceiveTransferUseCase (→ Movement IN)
  - [ ] GetStockByWarehouseUseCase
- [ ] Actualizar sales y purchases para especificar warehouse
- [ ] Tests de transferencias

**Entregables:**
- Precios dinámicos funcionando en ventas
- Promociones aplicándose automáticamente
- Multi-warehouse operativo
- Transferencias entre almacenes

### Fase 5: Reportes (Semana 8)

**Reportes Básicos:**
- [ ] Crear estructura reporting/ (solo app e infra, sin domain)
- [ ] Implementar queries agregadas:
  - [ ] SalesByPeriodQuery
  - [ ] TopProductsQuery
  - [ ] TopCustomersQuery
  - [ ] StockValueQuery
  - [ ] LowStockQuery
  - [ ] InventoryTurnoverQuery
  - [ ] PurchasesBySupplierQuery
  - [ ] AccountsReceivableQuery
- [ ] Controller y routes para reportes
- [ ] Exportación a CSV (opcional)
- [ ] Tests de queries

**Entregables:**
- Dashboard de reportes funcionando
- Queries optimizadas
- Exportación de datos

---

## 🎨 Mejoras Arquitectónicas Simultáneas

### 1. Simplificar DI Container con Decoradores

**Problema actual:** Registration manual verboso (370 líneas)

**Solución:**
```python
# shared/infra/di/decorators.py
def singleton(cls):
    container.register(cls, scope=LifetimeScope.SINGLETON)
    return cls

def scoped(cls):
    container.register(cls, scope=LifetimeScope.SCOPED)
    return cls

def transient(cls):
    container.register(cls, scope=LifetimeScope.TRANSIENT)
    return cls

# Uso:
@singleton
class ProductMapper(Mapper[Product, ProductModel]):
    def to_entity(self, model):
        ...

@scoped
class CreateSaleUseCase:
    def __init__(self, sale_repo: Repository[Sale]):
        self.sale_repo = sale_repo
```

### 2. Domain Events

**Para qué:** Desacoplar módulos (sales no debe conocer inventory directamente)

**Implementación:**
```python
# shared/domain/events.py
from abc import ABC
from datetime import datetime
from typing import List

class DomainEvent(ABC):
    occurred_at: datetime = datetime.now()

class SaleConfirmed(DomainEvent):
    sale_id: int
    items: List[dict]  # {product_id, quantity, warehouse_id}

class SaleCancelled(DomainEvent):
    sale_id: int
    items: List[dict]

class PurchaseReceived(DomainEvent):
    purchase_id: int
    items: List[dict]

class StockLevelLow(DomainEvent):
    product_id: int
    warehouse_id: int
    current_stock: int
    min_stock: int

# shared/infra/events/event_bus.py
class EventBus:
    _handlers = {}

    @classmethod
    def subscribe(cls, event_type, handler):
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent):
        event_type = type(event)
        if event_type in cls._handlers:
            for handler in cls._handlers[event_type]:
                handler(event)

# Uso en sales/app/use_cases/confirm_sale.py
class ConfirmSaleUseCase:
    def execute(self, sale_id: int):
        sale = self.sale_repo.get_by_id(sale_id)
        sale.status = SaleStatus.CONFIRMED
        self.sale_repo.update(sale)

        # Emitir evento
        event_bus.publish(SaleConfirmed(
            sale_id=sale.id,
            items=[{
                'product_id': item.product_id,
                'quantity': item.quantity,
                'warehouse_id': sale.warehouse_id
            } for item in sale.items]
        ))

# inventory/infra/event_handlers.py
@event_handler(SaleConfirmed)
def handle_sale_confirmed(event: SaleConfirmed):
    create_movement = container.resolve(CreateMovementUseCase)
    for item in event.items:
        create_movement.execute(
            product_id=item['product_id'],
            warehouse_id=item['warehouse_id'],
            type=MovementType.OUT,
            quantity=item['quantity'],
            reference_type='SALE',
            reference_id=event.sale_id
        )
```

### 3. Value Objects

**Para qué:** Encapsular lógica de validación y comportamiento

**Implementación:**
```python
# shared/domain/value_objects.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        return Money(self.amount * Decimal(str(factor)), self.currency)

@dataclass(frozen=True)
class TaxId:
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Invalid tax ID: {self.value}")

    def _is_valid(self) -> bool:
        # Implementar validación según país
        return len(self.value) >= 10

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if '@' not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

# Uso en entities:
@dataclass
class Customer(Entity):
    name: str
    tax_id: TaxId
    email: Email
    credit_limit: Money
```

### 4. Specifications Pattern

**Para qué:** Queries complejas reutilizables

**Implementación:**
```python
# shared/domain/specifications.py
from abc import ABC, abstractmethod

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, entity):
        pass

    @abstractmethod
    def to_sql_criteria(self):
        pass

    def __and__(self, other):
        return AndSpecification(self, other)

    def __or__(self, other):
        return OrSpecification(self, other)

class AndSpecification(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_sql_criteria(self):
        return [*self.left.to_sql_criteria(), *self.right.to_sql_criteria()]

# catalog/domain/specifications.py
class ProductInStock(Specification):
    def to_sql_criteria(self):
        return [Stock.quantity > 0]

class ProductInCategory(Specification):
    def __init__(self, category_id: int):
        self.category_id = category_id

    def to_sql_criteria(self):
        return [Product.category_id == self.category_id]

class ProductPriceBetween(Specification):
    def __init__(self, min_price, max_price):
        self.min = min_price
        self.max = max_price

    def to_sql_criteria(self):
        return [ProductPrice.base_price.between(self.min, self.max)]

# Uso:
spec = ProductInStock() & ProductInCategory(5) & ProductPriceBetween(10, 50)
products = product_repo.filter_by_spec(spec)
```

### 5. Repository con Specifications

```python
# shared/infra/repositories.py (mejorado)
class BaseRepository(Repository[E], Generic[E]):
    def filter_by_spec(
        self,
        spec: Specification,
        order_by: Optional[str] = None,
        desc_order: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[E]:
        criteria = spec.to_sql_criteria()
        models = self.filter(criteria, order_by, desc_order, limit, offset)
        return [self.mapper.to_entity(m) for m in models]
```

---

## 📊 Cambios en Base de Datos

### Nuevas Tablas

```sql
-- Customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    tax_id VARCHAR(32) UNIQUE,
    email VARCHAR(128),
    phone VARCHAR(32),
    address TEXT,
    city VARCHAR(64),
    state VARCHAR(64),
    country VARCHAR(64),
    customer_type VARCHAR(16),  -- RETAIL, WHOLESALE
    credit_limit DECIMAL(12, 2),
    payment_terms INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customer_contacts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(128),
    role VARCHAR(64),
    email VARCHAR(128),
    phone VARCHAR(32)
);

-- Sales
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    sale_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(16),  -- DRAFT, CONFIRMED, INVOICED, CANCELLED
    subtotal DECIMAL(12, 2),
    tax DECIMAL(12, 2),
    discount DECIMAL(12, 2),
    total DECIMAL(12, 2),
    payment_status VARCHAR(16),  -- PENDING, PARTIAL, PAID
    notes TEXT,
    created_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2),
    discount DECIMAL(12, 2),
    subtotal DECIMAL(12, 2)
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE,
    payment_date TIMESTAMP DEFAULT NOW(),
    amount DECIMAL(12, 2),
    payment_method VARCHAR(16),  -- CASH, CARD, TRANSFER, CREDIT
    reference VARCHAR(128),
    notes TEXT
);

-- Suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    tax_id VARCHAR(32) UNIQUE,
    email VARCHAR(128),
    phone VARCHAR(32),
    address TEXT,
    payment_terms INTEGER,
    lead_time_days INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    supplier_sku VARCHAR(64),
    cost_price DECIMAL(12, 2),
    min_order_qty INTEGER,
    UNIQUE(supplier_id, product_id)
);

-- Purchases
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    supplier_id INTEGER REFERENCES suppliers(id),
    order_date TIMESTAMP DEFAULT NOW(),
    expected_date TIMESTAMP,
    status VARCHAR(16),  -- DRAFT, SENT, RECEIVED, CANCELLED
    subtotal DECIMAL(12, 2),
    tax DECIMAL(12, 2),
    total DECIMAL(12, 2),
    notes TEXT
);

CREATE TABLE purchase_order_items (
    id SERIAL PRIMARY KEY,
    purchase_order_id INTEGER REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(12, 2),
    subtotal DECIMAL(12, 2),
    received_quantity INTEGER DEFAULT 0
);

CREATE TABLE purchase_receipts (
    id SERIAL PRIMARY KEY,
    purchase_order_id INTEGER REFERENCES purchase_orders(id),
    receipt_date TIMESTAMP DEFAULT NOW(),
    received_by VARCHAR(64),
    notes TEXT
);

-- Pricing
CREATE TABLE price_lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    currency VARCHAR(8) DEFAULT 'USD',
    is_default BOOLEAN DEFAULT FALSE,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP
);

CREATE TABLE product_prices (
    id SERIAL PRIMARY KEY,
    price_list_id INTEGER REFERENCES price_lists(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    base_price DECIMAL(12, 2),
    discount_percent DECIMAL(5, 2),
    min_quantity INTEGER DEFAULT 1,
    customer_type VARCHAR(16),
    UNIQUE(price_list_id, product_id, min_quantity, customer_type)
);

CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128),
    promotion_type VARCHAR(16),  -- DISCOUNT, BUNDLE, BUY_X_GET_Y
    value DECIMAL(12, 2),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    applicable_to VARCHAR(16)  -- PRODUCTS, CATEGORIES, ALL
);

-- Warehouses
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    address TEXT,
    is_main BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Modificar stock (agregar warehouse_id)
ALTER TABLE stock ADD COLUMN warehouse_id INTEGER REFERENCES warehouses(id);
CREATE INDEX idx_stock_warehouse ON stock(warehouse_id);

-- Modificar movements (agregar warehouse_id)
ALTER TABLE movements ADD COLUMN warehouse_id INTEGER REFERENCES warehouses(id);
CREATE INDEX idx_movements_warehouse ON movements(warehouse_id);

-- Transfers
CREATE TABLE stock_transfers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    from_warehouse_id INTEGER REFERENCES warehouses(id),
    to_warehouse_id INTEGER REFERENCES warehouses(id),
    transfer_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(16),  -- PENDING, IN_TRANSIT, RECEIVED
    notes TEXT
);

CREATE TABLE stock_transfer_items (
    id SERIAL PRIMARY KEY,
    transfer_id INTEGER REFERENCES stock_transfers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL
);
```

### Índices Importantes

```sql
-- Performance indexes
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_status ON sales(status);
CREATE INDEX idx_sale_items_product ON sale_items(product_id);

CREATE INDEX idx_movements_date ON movements(date);
CREATE INDEX idx_movements_product ON movements(product_id);
CREATE INDEX idx_movements_reference ON movements(reference_type, reference_id);

CREATE INDEX idx_stock_product ON stock(product_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);

CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
```

---

## 🎯 KPIs y Métricas de Éxito

### Por Fase

**Fase 1 (Preparación):**
- ✅ 0 errores de importación
- ✅ Todos los tests pasando
- ✅ Cobertura de tests > 60%

**Fase 2 (Clientes + Ventas):**
- ✅ CRUD de clientes funcionando
- ✅ Crear y confirmar venta actualiza stock
- ✅ Anular venta revierte stock
- ✅ Tests de integración pasando

**Fase 3 (Proveedores + Compras):**
- ✅ CRUD de proveedores funcionando
- ✅ Recibir compra actualiza stock
- ✅ Flujo completo de reabastecimiento

**Fase 4 (Pricing + Warehouse):**
- ✅ Precios por lista de precios
- ✅ Promociones aplicándose
- ✅ Multi-warehouse operativo
- ✅ Transferencias funcionando

**Fase 5 (Reporting):**
- ✅ 8+ reportes funcionando
- ✅ Queries optimizadas (< 500ms)
- ✅ Exportación a CSV

---

## 📚 Recursos y Referencias

### Arquitectura
- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)
- Implementing Domain-Driven Design (Vaughn Vernon)

### Patrones
- Repository Pattern
- Specification Pattern
- Domain Events
- Value Objects
- Use Cases / Interactors

### Tecnologías
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/

---

## 🚀 Próximos Pasos Inmediatos

1. ✅ **HOY**: Arreglar 4 bugs críticos
2. 📅 **Mañana**: Decidir si refactorizar estructura o empezar con customers
3. 📅 **Esta semana**: Completar Fase 1 (preparación)
4. 📅 **Próximas 2 semanas**: Implementar customers + sales

---

**Última actualización:** 2026-02-02
**Versión:** 1.0
**Autor:** Planning Session con Claude Code
