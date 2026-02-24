# POS API — Plan de Desarrollo Completo

**Fecha**: 2026-02-24
**Branch**: master
**Estado del módulo**: `src/pos/` — parcialmente implementado

---

## 1. Estado Actual

### Archivos y endpoints activos (montados en `main.py`)

| Router | Prefijo | Montado en `main.py` |
|---|---|---|
| `AdminSaleRouter` (`admin_routes.py`) | `/api/admin/sales` | ✅ Sí — solo GET |
| `POSSaleRouter` (`pos/sales/infra/routes.py`) | `/api/pos/sales` | ✅ Sí — full CRUD + confirm/cancel |
| `POSProductRouter` | `/api/pos/products` | ✅ Sí — solo GET |
| `POSCustomerRouter` | `/api/pos/customers` | ✅ Sí — solo GET |

### Endpoints activos en `/api/pos/`

```
POST   /api/pos/sales/                        Crear venta (DRAFT)
GET    /api/pos/sales/{id}                    Ver venta
POST   /api/pos/sales/{id}/items              Agregar ítem
GET    /api/pos/sales/{id}/items              Listar ítems
DELETE /api/pos/sales/{id}/items/{item_id}    Quitar ítem
POST   /api/pos/sales/{id}/confirm            Confirmar + inventario (atómico)
POST   /api/pos/sales/{id}/cancel             Cancelar + revertir stock (atómico)
POST   /api/pos/sales/{id}/payments           Registrar pago
GET    /api/pos/sales/{id}/payments           Listar pagos
GET    /api/pos/products/                     Listar productos
GET    /api/pos/products/{id}                 Ver producto
GET    /api/pos/customers/                    Listar clientes
GET    /api/pos/customers/{id}                Ver cliente
GET    /api/pos/customers/search/by-tax-id    Buscar por RUC
```

### Diferencia clave: POS vs Admin

| Aspecto | POS | Admin |
|---|---|---|
| Confirm | **Atómico**: verifica stock, crea movimientos OUT, actualiza stock, publica evento | **Event-driven**: publica `SaleConfirmed`, el event handler hace el resto |
| Cancel | **Atómico**: crea movimientos IN, restaura stock, publica evento | **Event-driven**: publica `SaleCancelled`, el event handler revierte |

---

## 2. Dead Code — Limpieza requerida (Fase 0)

### Hallazgo

`src/sales/infra/routes.py` contiene `SaleRouter` — un router con CRUD completo de ventas incluyendo confirm/cancel usando los handlers event-driven del módulo admin. **Este router nunca se monta en `main.py`** y por tanto ningún endpoint de él es accesible.

Como consecuencia, `ConfirmSaleCommandHandler` y `CancelSaleCommandHandler` están registrados en el DI container (`sales/infra/container.py`) pero **ningún endpoint activo los usa**.

### Archivos afectados

| Archivo | Problema |
|---|---|
| `src/sales/infra/routes.py` | `SaleRouter` — clase completa muerta, nunca importada por `main.py` |
| `src/sales/infra/container.py` | `ConfirmSaleCommandHandler`, `CancelSaleCommandHandler` registrados sin uso activo |
| `src/sales/app/commands/__init__.py` | Exporta `ConfirmSaleCommandHandler`, `CancelSaleCommandHandler` — sin consumidor activo |

### Acción de limpieza

1. **Eliminar** `src/sales/infra/routes.py` completamente
2. **Eliminar** de `src/sales/infra/container.py`:
   - `ConfirmSaleCommandHandler`
   - `CancelSaleCommandHandler`
3. **Eliminar** de `src/sales/app/commands/__init__.py` las exportaciones de ambos handlers
4. **Opcional** (decidir antes): ¿Se eliminan también `confirm_sale.py` y `cancel_sale.py` de `src/sales/app/commands/`?
   - **Sí, eliminar** si la decisión de diseño es que confirmación/cancelación de ventas solo ocurre por POS (atómico)
   - **No eliminar** si en el futuro se quiere agregar un endpoint admin de mutación de ventas

> **Decisión recomendada**: eliminar los archivos. La confirmación atómica del POS es el patrón correcto. Si se necesita un flujo admin de confirmación en el futuro, se puede crear un nuevo handler con el patrón correcto.

---

## 3. Arquitectura del módulo POS

```
src/pos/
├── __init__.py
├── infra/
│   ├── routes.py              ← POSProductRouter, POSCustomerRouter
│   └── container.py           ← INJECTABLES de todos los sub-módulos POS
└── sales/
    ├── app/
    │   ├── commands/
    │   │   ├── confirm_sale.py    ← POSConfirmSaleCommandHandler (atómico)
    │   │   └── cancel_sale.py     ← POSCancelSaleCommandHandler (atómico)
    │   └── queries/               ← (vacío — reutiliza queries de src/sales/)
    └── infra/
        ├── routes.py              ← POSSaleRouter
        ├── validators.py          ← (vacío — reutiliza validators de src/sales/)
        └── container.py           ← POS_SALES_INJECTABLES
```

**Patrón POS**: verificar estado → actuar sobre entidades → persistir directamente → publicar evento. No delegar a event handlers para operaciones críticas de stock.

---

## 4. Backlog — Features nuevas por fase

### Fase 1 — Búsqueda optimizada para POS

**Objetivo**: El cajero necesita encontrar productos rápido (por nombre, SKU) y ver stock disponible antes de agregar al carrito.

#### 1.1 Búsqueda de productos con stock

**Nuevo endpoint**: `GET /api/pos/products/search?q=&location_id=`

**Nuevo handler**: `src/pos/products/app/queries/search_products.py`

```python
@dataclass
class POSSearchProductsQuery(Query):
    q: str
    location_id: int | None = None
    limit: int = 20
```

**Nuevo validator** en `src/pos/products/infra/validators.py`:
```python
class POSProductResponse:
    id, sku, name
    unit_price: Decimal        # de Product (requiere Fase 0.1)
    available_stock: Decimal   # JOIN con stock filtrado por location_id
    uom_name: str              # nombre de la unidad de medida
```

**Dependencias**: `ProductRepository`, `StockRepository`
**Nota**: Requiere que `Product` tenga campo `unit_price` (ver sección 5.1)

#### 1.2 Búsqueda de clientes por nombre o RUC

**Nuevo endpoint**: `GET /api/pos/customers/search?q=`

Actualmente existe `GET /api/pos/customers/search/by-tax-id` que busca por RUC exacto. Reemplazar/extender con búsqueda parcial por nombre o RUC.

**Nuevo handler**: `src/pos/customers/app/queries/search_customers.py`

```python
@dataclass
class POSSearchCustomersQuery(Query):
    q: str
    limit: int = 10
```

#### 1.3 Creación rápida de cliente desde POS

**Nuevo endpoint**: `POST /api/pos/customers/`

Reusar `CreateCustomerCommandHandler` de `src/customers/`. Solo campos mínimos: nombre, RUC (opcional), teléfono (opcional).

---

### Fase 2 — Checkout y pagos enriquecidos

**Objetivo**: Express checkout en una sola llamada y respuesta de pago con vuelto calculado.

#### 2.1 Respuesta de pago con cambio (vuelto)

Modificar el response de `POST /api/pos/sales/{id}/payments` para incluir:

```python
class POSPaymentResponse:
    id, sale_id, amount, payment_method, payment_date
    total_paid: Decimal      # suma de todos los pagos de la venta
    sale_total: Decimal      # total de la venta
    change: Decimal          # max(0, total_paid - sale_total)
    payment_status: str      # PENDING / PARTIAL / PAID
```

Crear `src/pos/sales/infra/validators.py` con este schema POS-específico.
La ruta de `POST /{sale_id}/payments` en `POSSaleRouter` debe retornar este schema.

#### 2.2 Express checkout (confirm + pago en un paso)

**Nuevo endpoint**: `POST /api/pos/sales/{id}/checkout`

Combina confirm atómico + registro de pago(s) en una sola llamada.

**Nuevo handler**: `src/pos/sales/app/commands/checkout.py`

```python
@dataclass
class POSCheckoutCommand(Command):
    sale_id: int
    payments: list[dict]   # [{payment_method, amount}, ...]

class POSCheckoutCommandHandler(CommandHandler):
    # 1. Ejecuta lógica de POSConfirmSaleCommandHandler
    # 2. Registra cada pago via RegisterPaymentCommandHandler
    # 3. Retorna {sale, payments, change}
```

---

### Fase 3 — Sesión de caja

**Objetivo**: Control de apertura/cierre de caja, efectivo inicial, cuadre al cierre.

#### 3.1 Estructura del módulo

```
src/pos/session/
├── domain/
│   ├── entities.py     ← POSSession, SessionStatus
│   └── events.py       ← SessionOpened, SessionClosed
├── app/
│   ├── commands/
│   │   ├── open_session.py    ← OpenSessionCommandHandler
│   │   └── close_session.py   ← CloseSessionCommandHandler
│   └── queries/
│       ├── get_active_session.py
│       └── get_session_summary.py
└── infra/
    ├── models.py
    ├── mappers.py
    ├── repositories.py
    ├── routes.py
    ├── validators.py
    └── container.py
```

#### 3.2 Entidad

```python
class SessionStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

@dataclass
class POSSession(Entity):
    id: int
    cashier_id: str           # usuario que abre la caja
    opening_amount: Decimal   # efectivo inicial declarado
    closing_amount: Decimal | None
    status: SessionStatus
    opened_at: datetime
    closed_at: datetime | None
    notes: str | None
```

#### 3.3 Endpoints

```
POST  /api/pos/sessions/open         Abrir sesión de caja
POST  /api/pos/sessions/{id}/close   Cerrar sesión + cuadre
GET   /api/pos/sessions/active       Sesión activa actual
GET   /api/pos/sessions/{id}/summary Resumen: ventas, pagos por método, diferencia
```

**Migración requerida**: nueva tabla `pos_sessions`

---

### Fase 4 — Ticket / Recibo

**Objetivo**: Endpoint que devuelve datos estructurados del ticket para impresión (no genera PDF, el cliente lo formatea).

#### 4.1 Sale number correlativo

Agregar `sale_number` a `Sale` como correlativo legible (ej: `V-2025-00001`).
**Migración**: `ALTER TABLE sales ADD COLUMN sale_number VARCHAR UNIQUE`
Generar al crear la venta en `CreateSaleCommandHandler`.

#### 4.2 Endpoint ticket

**Nuevo endpoint**: `GET /api/pos/sales/{id}/ticket`

**Nuevo handler**: `src/pos/sales/app/queries/get_sale_ticket.py`

**Response**:
```python
class POSSaleTicketResponse:
    sale_number: str
    sale_date: datetime
    customer: CustomerInfo | None
    items: list[TicketItem]    # nombre, cantidad, precio_unit, subtotal
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    payments: list[PaymentInfo]
    change: Decimal
```

**Dependencias**: `SaleRepository`, `SaleItemRepository`, `PaymentRepository`, `ProductRepository`, `CustomerRepository`

---

### Fase 5 — Devoluciones / Reembolsos

**Objetivo**: Devolución parcial o total de ítems de una venta confirmada, con restauración de stock.

#### 5.1 Nuevas entidades en `src/sales/domain/`

```python
@dataclass
class SaleRefund(Entity):
    id: int
    sale_id: int
    reason: str
    refund_date: datetime
    total_refunded: Decimal
    created_by: str

@dataclass
class SaleRefundItem(Entity):
    id: int
    refund_id: int
    sale_item_id: int
    quantity: Decimal     # cantidad devuelta (≤ cantidad vendida)
    unit_price: Decimal
```

#### 5.2 Comando atómico POS

**Nuevo handler**: `src/pos/sales/app/commands/refund_sale.py`

Flujo:
1. Validar que la venta está CONFIRMED o INVOICED
2. Validar que las cantidades devueltas ≤ vendidas
3. Crear `SaleRefund` + `SaleRefundItem`s
4. Crear movimiento IN por cada ítem devuelto (stock restaurado — atómico)
5. Publicar evento `SaleRefunded`

**Nuevas migraciones**: tablas `sale_refunds`, `sale_refund_items`

**Endpoint**: `POST /api/pos/sales/{id}/refund`

---

### Fase 6 — Ventas en espera (Hold)

**Objetivo**: Pausar una venta activa para atender a otro cliente y retomarla después.

#### 6.1 Cambios en entidad `Sale`

Agregar campos: `is_on_hold: bool`, `hold_label: str | None`
**Migración**: `ALTER TABLE sales ADD COLUMN is_on_hold BOOLEAN DEFAULT FALSE, ADD COLUMN hold_label VARCHAR`

#### 6.2 Endpoints

```
POST /api/pos/sales/{id}/hold      Poner en espera (solo DRAFT)
POST /api/pos/sales/{id}/recall    Retomar venta
GET  /api/pos/sales/on-hold        Listar ventas en espera
```

---

### Fase 7 — Reporte diario / Z-Report

**Objetivo**: Resumen de caja al cierre del día o sesión.

**Nuevo endpoint**: `GET /api/pos/reports/daily-summary?date=&session_id=`

**Response**:
```python
class POSDailySummaryResponse:
    date: date
    session_id: int | None
    total_sales: int
    sales_by_status: dict        # {CONFIRMED: N, CANCELLED: M}
    gross_amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal
    payments_by_method: dict     # {CASH: X, CARD: Y, TRANSFER: Z}
    refunds_total: Decimal
    net_cash: Decimal            # efectivo en caja esperado
```

---

## 5. Cambios en el modelo de dominio existente

### 5.1 Agregar `unit_price` a `Product`

Actualmente `Product` no tiene precio de venta. Es necesario para que el POS muestre precios al buscar productos.

- **Entidad**: `src/catalog/product/domain/entities.py` — agregar `unit_price: Decimal | None = None`
- **Modelo**: `src/catalog/product/infra/models.py` — agregar columna
- **Migración**: `ALTER TABLE products ADD COLUMN unit_price NUMERIC(12,2)`

### 5.2 Nueva tabla `pos_sessions`

```sql
CREATE TABLE pos_sessions (
    id          SERIAL PRIMARY KEY,
    cashier_id  VARCHAR NOT NULL,
    opening_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    closing_amount NUMERIC(12,2),
    status      VARCHAR NOT NULL DEFAULT 'OPEN',
    opened_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    closed_at   TIMESTAMP,
    notes       TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 5.3 Columnas en `sales`

```sql
ALTER TABLE sales ADD COLUMN sale_number  VARCHAR UNIQUE;
ALTER TABLE sales ADD COLUMN is_on_hold   BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE sales ADD COLUMN hold_label   VARCHAR;
ALTER TABLE sales ADD COLUMN session_id   INTEGER REFERENCES pos_sessions(id);
```

### 5.4 Nuevas tablas `sale_refunds`, `sale_refund_items`

```sql
CREATE TABLE sale_refunds (
    id              SERIAL PRIMARY KEY,
    sale_id         INTEGER NOT NULL REFERENCES sales(id),
    reason          TEXT NOT NULL,
    refund_date     TIMESTAMP NOT NULL DEFAULT NOW(),
    total_refunded  NUMERIC(12,2) NOT NULL,
    created_by      VARCHAR NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE sale_refund_items (
    id              SERIAL PRIMARY KEY,
    refund_id       INTEGER NOT NULL REFERENCES sale_refunds(id),
    sale_item_id    INTEGER NOT NULL REFERENCES sale_items(id),
    quantity        NUMERIC(12,4) NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 6. Orden de implementación recomendado

```
Sesión 1:  Fase 0   — Limpieza de dead code (SaleRouter + handlers huérfanos)
Sesión 2:  Fase 0.1 — Agregar unit_price a Product (migración)
Sesión 3:  Fase 1   — Búsqueda productos con stock + búsqueda/creación de clientes
Sesión 4:  Fase 2   — Express checkout + response de pago con vuelto
Sesión 5:  Fase 4   — Ticket de venta + sale_number correlativo
Sesión 6:  Fase 3   — Sesión de caja (POSSession)
Sesión 7:  Fase 5   — Devoluciones/Reembolsos
Sesión 8:  Fase 6   — Ventas en espera (Hold)
Sesión 9:  Fase 7   — Z-Report diario
```

---

## 7. Convenciones del proyecto

- **Rutas**: endpoints POS bajo `/api/pos/...`; registrar en `main.py`
- **DI**: nuevos handlers/repos van en `infra/container.py` del módulo → agregar al `INJECTABLES` de `src/container.py`
- **Handlers**: comandos extienden `CommandHandler[TCmd, TResult]`; queries extienden `QueryHandler[TQuery, TResult]`
- **Validators**: Pydantic con `model_config = ConfigDict(populate_by_name=True)` y alias camelCase
- **Errores**: `DomainError` para reglas de negocio, `NotFoundError` para recursos no encontrados
- **Migraciones**: `make migrations m="descripción"` → `make upgrade`
- **Tests**: `make tests` (Docker) o `.venv/bin/python -m pytest tests/ -v`
- **Linter**: `make lint` (ruff)
- **Commits**: conventional commits — `feat:`, `fix:`, `refactor:`, `chore:`

---

## 8. Checklist de progreso

### Fase 0 — Limpieza (Dead Code) ✅ COMPLETADA
- [x] Eliminar `src/sales/infra/routes.py` (`SaleRouter`)
- [x] Eliminar `ConfirmSaleCommandHandler`, `CancelSaleCommandHandler` de `sales/infra/container.py`
- [x] Limpiar exportaciones en `src/sales/app/commands/__init__.py`
- [x] Eliminar `confirm_sale.py` y `cancel_sale.py` de `src/sales/app/commands/` (patrón POS atómico es el correcto)
- [x] Eliminar tests huérfanos de `ConfirmSaleCommandHandler` y `CancelSaleCommandHandler` en `tests/unit/sales/test_commands.py`
- [x] Verificar que `make lint` y tests pasen (584 tests, 0 errores)

### Fase 0.1 — unit_price en Product
- [ ] Agregar `unit_price` a entidad `Product`
- [ ] Agregar columna en `ProductModel`
- [ ] Migración
- [ ] Validar en validators de producto

### Fase 1 — Búsqueda POS
- [ ] `POSSearchProductsQuery` + handler con stock disponible
- [ ] Validator `POSProductResponse` con stock y precio
- [ ] Endpoint `GET /api/pos/products/search`
- [ ] `POSSearchCustomersQuery` + handler búsqueda parcial
- [ ] Endpoint `GET /api/pos/customers/search`
- [ ] Endpoint `POST /api/pos/customers/` (creación rápida)
- [ ] Registrar en container + routes + main.py

### Fase 2 — Checkout express
- [ ] Validator `POSPaymentResponse` con cambio calculado en `pos/sales/infra/validators.py`
- [ ] Actualizar `POSSaleRouter.register_payment` para retornar `POSPaymentResponse`
- [ ] `POSCheckoutCommand` + handler
- [ ] Validator request/response de checkout
- [ ] Endpoint `POST /api/pos/sales/{id}/checkout`
- [ ] Registrar en container + routes

### Fase 3 — Sesión de caja
- [ ] Entidad `POSSession` + `SessionStatus`
- [ ] Eventos `SessionOpened`, `SessionClosed`
- [ ] `OpenSessionCommand` + handler
- [ ] `CloseSessionCommand` + handler
- [ ] `GetActiveSessionQuery` + handler
- [ ] `GetSessionSummaryQuery` + handler
- [ ] Modelo `POSSessionModel` + mapper + repository
- [ ] Validators + routes
- [ ] Migración `pos_sessions`
- [ ] Registrar en container + main.py

### Fase 4 — Ticket
- [ ] `sale_number` correlativo en `Sale` + `SaleModel`
- [ ] Migración columna `sale_number`
- [ ] Generar `sale_number` en `CreateSaleCommandHandler`
- [ ] `GetSaleTicketQuery` + handler
- [ ] Validator `POSSaleTicketResponse`
- [ ] Endpoint `GET /api/pos/sales/{id}/ticket`
- [ ] Registrar en container + routes

### Fase 5 — Devoluciones
- [ ] Entidades `SaleRefund` + `SaleRefundItem` en `src/sales/domain/`
- [ ] Evento `SaleRefunded` en `src/sales/domain/events.py`
- [ ] `RefundSaleCommand` + handler POS (atómico) en `src/pos/sales/app/commands/`
- [ ] Modelos SQLAlchemy + mapper + repository en `src/sales/infra/`
- [ ] Validators + endpoint `POST /api/pos/sales/{id}/refund`
- [ ] Migraciones `sale_refunds`, `sale_refund_items`
- [ ] Registrar en container + routes

### Fase 6 — Hold
- [ ] Campos `is_on_hold`, `hold_label` en `Sale` y `SaleModel`
- [ ] Migración
- [ ] `HoldSaleCommand` + handler
- [ ] `RecallSaleCommand` + handler
- [ ] `GetOnHoldSalesQuery` + handler
- [ ] Endpoints hold/recall/on-hold

### Fase 7 — Z-Report
- [ ] `GetDailySummaryQuery` + handler
- [ ] Validator `POSDailySummaryResponse`
- [ ] Endpoint `GET /api/pos/reports/daily-summary`
- [ ] Registrar en container + routes + main.py

---

## 9. Contexto para retomar en nuevas sesiones

Al iniciar una nueva sesión, leer:
1. Este documento (`docs/pos-plan.md`) — estado y checklist
2. `src/pos/sales/app/commands/confirm_sale.py` — patrón de comando POS atómico de referencia
3. `src/sales/domain/entities.py` — entidades de dominio actuales
4. `src/sales/infra/container.py` — patrón de registro DI
5. `src/pos/sales/infra/routes.py` — patrón de rutas POS
6. `src/container.py` — cómo se agregan módulos al container global
7. `main.py` — cómo se registran los routers

Verificar el checklist de esta sección para saber en qué fase se quedó el desarrollo.
