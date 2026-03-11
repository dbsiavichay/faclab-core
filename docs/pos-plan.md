# Plan de Desarrollo POS - Faclab Core

## Contexto

El sistema ya tiene un MVP del API administrativa (catalogo, inventario, compras, ventas, clientes, proveedores, reportes). El modulo POS (`src/pos/`) tiene una implementacion parcial: CRUD de ventas, confirm/cancel atomicos con inventario, consulta de productos y clientes. Este plan cubre las funcionalidades faltantes para un punto de venta completo, organizado en sesiones ejecutables con Claude Code.

**Decisiones clave:**
- Consumidor Final para ventas anonimas: **SI** (bandera `is_final_consumer` en Sale, `customer_id` nullable)
- Facturacion electronica SRI: **NO por ahora**
- Turno obligatorio para ventas POS: **SI**
- Actualizar cantidad de items existentes: **SI**

---

## Sesion 1: Gestion de Turnos (Shifts)

**Objetivo:** Crear el submodulo `pos/shift` — fundamento de todas las operaciones POS.

### Entidades
- `Shift`: `id`, `cashier_name`, `opened_at`, `closed_at`, `opening_balance: Decimal`, `closing_balance: Decimal | None`, `expected_balance: Decimal | None`, `discrepancy: Decimal | None`, `status: ShiftStatus`, `notes`
- `ShiftStatus`: `OPEN`, `CLOSED`

### Estructura de archivos
```
src/pos/shift/
├── domain/
│   ├── entities.py        # Shift, ShiftStatus
│   ├── events.py          # ShiftOpened, ShiftClosed
│   └── exceptions.py      # ShiftAlreadyOpenError, NoOpenShiftError
├── app/
│   ├── commands/
│   │   ├── open_shift.py  # OpenShiftCommand + Handler
│   │   └── close_shift.py # CloseShiftCommand + Handler
│   └── queries/
│       └── get_shifts.py  # GetActiveShift, GetShiftById, GetAllShifts
└── infra/
    ├── models.py          # ShiftModel -> tabla pos_shifts
    ├── mappers.py         # ShiftMapper
    ├── repositories.py    # ShiftRepository
    ├── validators.py      # OpenShiftRequest, CloseShiftRequest, ShiftResponse
    ├── routes.py          # POSShiftRouter
    └── container.py       # INJECTABLES
```

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/shifts/open` | Abrir turno (valida que no haya otro abierto) |
| POST | `/api/pos/shifts/{id}/close` | Cerrar turno (calcula balance esperado y discrepancia) |
| GET | `/api/pos/shifts/active` | Obtener turno activo |
| GET | `/api/pos/shifts/{id}` | Obtener turno por ID |
| GET | `/api/pos/shifts` | Listar turnos (paginado) |

### Reglas de negocio
- Solo puede haber un turno OPEN a la vez
- Al cerrar: `expected_balance = opening_balance + ventas_efectivo - devoluciones_efectivo`
- `discrepancy = closing_balance - expected_balance`

### Registro
- `src/pos/shift/infra/container.py` -> INJECTABLES en `src/container.py`
- `POSShiftRouter` en `main.py` bajo `pos_router`

### Tests
- `tests/unit/pos/shift/test_entities.py` — open, close, discrepancia
- `tests/unit/pos/shift/test_commands.py` — OpenShift, CloseShift
- `tests/unit/pos/shift/test_queries.py` — GetActiveShift, GetAll

### Migracion
`make migrations m="create pos_shifts table"`

---

## Sesion 2: Busqueda de Productos + Crear Cliente Rapido

**Objetivo:** Busqueda rapida por SKU/barcode/nombre y creacion rapida de clientes desde POS.

### Busqueda de productos
- Nueva query `SearchProductsQuery(term, limit=20)` en `src/catalog/product/app/queries/search_products.py`
- Busca por: SKU (exact), barcode (exact), nombre (ILIKE)
- Product ya tiene campo `barcode` en entidad y modelo

### Crear cliente rapido
- Reusar `CreateCustomerCommandHandler` del modulo customers
- Agregar `POST /api/pos/customers` con validador `QuickCustomerRequest` (campos minimos: name, taxId, taxType)

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/pos/products/search?term=...` | Busqueda por SKU/barcode/nombre |
| POST | `/api/pos/customers` | Crear cliente rapido |

### Archivos a crear/modificar
- `src/catalog/product/app/queries/search_products.py` — nueva query
- `src/catalog/product/infra/container.py` — registrar handler
- `src/pos/infra/routes.py` — agregar search a POSProductRouter, POST a POSCustomerRouter
- `src/pos/infra/validators.py` — nuevo archivo, QuickCustomerRequest

### Tests
- `tests/unit/catalog/product/test_search.py`
- `tests/unit/pos/test_quick_customer.py`

---

## Sesion 3: Actualizar Items + Vincular Ventas a Turno + Consumidor Final

**Objetivo:** Permitir actualizar cantidad/descuento de items existentes. Vincular ventas al turno activo obligatoriamente. Soporte para ventas a Consumidor Final.

### Actualizar item
- Nuevo command `UpdateSaleItemCommand(sale_id, item_id, quantity?, discount?)` en `src/sales/app/commands/update_sale_item.py`
- Handler: valida que la venta este en DRAFT, actualiza campos, recalcula totales de la venta
- Nuevo endpoint en POS routes

### Vincular ventas a turno
- Agregar `shift_id: int | None` a entidad `Sale` y `SaleModel`
- Modificar POS `create_sale` route para obtener turno activo y pasar `shift_id`
- Modificar `POSConfirmSaleCommandHandler` para validar que el turno sigue abierto
- Migracion para agregar columna `shift_id` con FK a `pos_shifts`

### Consumidor Final (bandera en Sale)
- Agregar `is_final_consumer: bool = False` a entidad `Sale` y `SaleModel`
- Hacer `customer_id: int | None` nullable (actualmente es `int` obligatorio)
- Cuando `is_final_consumer=True`, `customer_id` es `None` — no se requiere cliente registrado
- Para recibos/reportes se muestra "Consumidor Final" / "9999999999999" como datos de presentacion
- Modificar `CreateSaleCommand` para aceptar `is_final_consumer` y hacer `customer_id` opcional
- Validacion: si `is_final_consumer=False`, `customer_id` es obligatorio

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| PUT | `/api/pos/sales/{sale_id}/items/{item_id}` | Actualizar cantidad/descuento |

### Archivos a crear/modificar
- `src/sales/app/commands/update_sale_item.py` — nuevo
- `src/sales/app/commands/create_sale.py` — hacer customer_id opcional, agregar is_final_consumer
- `src/sales/domain/entities.py` — agregar shift_id, is_final_consumer; customer_id nullable
- `src/sales/infra/models.py` — agregar shift_id FK, is_final_consumer, customer_id nullable
- `src/sales/infra/validators.py` — actualizar SaleRequest y SaleResponse
- `src/sales/infra/container.py` — registrar handler
- `src/pos/sales/infra/routes.py` — agregar endpoint update item
- `src/pos/sales/app/commands/confirm_sale.py` — validar turno abierto

### Tests
- `tests/unit/sales/test_update_item.py`
- `tests/unit/pos/sales/test_confirm_with_shift.py`
- `tests/unit/sales/test_create_sale_final_consumer.py`

### Migracion
`make migrations m="add shift_id is_final_consumer to sales make customer_id nullable"`

---

## Sesion 4: Hold/Park Sales (Aparcar Ventas)

**Objetivo:** Guardar ventas para despues (cliente olvido billetera, etc.) y retomarlas.

### Modificaciones a Sale
- Agregar campos a `Sale`: `parked_at: datetime | None`, `park_reason: str | None`
- Metodos: `park(reason?)` — solo desde DRAFT, `resume()` — limpia parked_at

### Commands y queries
- `ParkSaleCommand(sale_id, reason?)` / handler
- `ResumeSaleCommand(sale_id)` / handler
- `GetParkedSalesQuery` / handler — DRAFT con `parked_at IS NOT NULL`

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/sales/{sale_id}/park` | Aparcar venta |
| POST | `/api/pos/sales/{sale_id}/resume` | Retomar venta |
| GET | `/api/pos/sales/parked` | Listar ventas aparcadas |

### Archivos a crear/modificar
- `src/sales/domain/entities.py` — agregar park/resume + campos
- `src/sales/infra/models.py` — agregar columnas
- `src/sales/infra/validators.py` — actualizar SaleResponse
- `src/pos/sales/app/commands/park_sale.py` — nuevo
- `src/pos/sales/app/commands/resume_sale.py` — nuevo
- `src/pos/sales/app/queries/get_parked_sales.py` — nuevo
- `src/pos/sales/infra/routes.py` — agregar endpoints
- `src/pos/sales/infra/container.py` — registrar handlers

### Tests
- `tests/unit/sales/test_entities.py` — park() y resume()
- `tests/unit/pos/sales/test_park_sale.py`
- `tests/unit/pos/sales/test_resume_sale.py`

### Migracion
`make migrations m="add parked_at park_reason to sales"`

---

## Sesion 5: Descuentos y Calculo de Impuestos (IVA Ecuador)

**Objetivo:** Descuentos a nivel de venta, calculo automatico de IVA (12% / 0%).

### Impuestos
- Agregar `tax_rate: Decimal = Decimal("12.00")` a `Product` entity y model
- Agregar `tax_rate: Decimal`, `tax_amount: Decimal` a `SaleItem` entity y model
- Al agregar item, se toma el `tax_rate` del producto y se calcula: `tax_amount = subtotal * tax_rate / 100`

### Descuentos a nivel de venta
- Agregar a `Sale`: `discount_type: str | None` (PERCENTAGE o AMOUNT), `discount_value: Decimal = 0`
- Nuevo command: `ApplySaleDiscountCommand(sale_id, discount_type, discount_value)`
- La logica de recalculo se centraliza en un servicio de dominio `recalculate_sale_totals()` en `src/sales/domain/services.py`

### Recalculo de totales
```python
def recalculate_sale_totals(items, discount_type, discount_value):
    subtotal = sum(item.subtotal for item in items)  # despues de descuento por item
    tax = sum(item.tax_amount for item in items)
    if discount_type == "PERCENTAGE":
        discount = subtotal * discount_value / 100
    else:
        discount = discount_value
    total = subtotal + tax - discount
    return {"subtotal": subtotal, "tax": tax, "discount": discount, "total": total}
```

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/sales/{sale_id}/discount` | Aplicar descuento a nivel de venta |

### Archivos a crear/modificar
- `src/catalog/product/domain/entities.py` — agregar tax_rate
- `src/catalog/product/infra/models.py` — agregar columna tax_rate
- `src/sales/domain/entities.py` — agregar tax_rate/tax_amount a SaleItem, discount_type/value a Sale
- `src/sales/domain/services.py` — nuevo, recalculate_sale_totals
- `src/sales/infra/models.py` — agregar columnas
- `src/sales/infra/validators.py` — actualizar responses
- `src/sales/app/commands/add_sale_item.py` — usar tax_rate del producto
- `src/pos/sales/app/commands/apply_discount.py` — nuevo
- Modificar todos los commands que cambian items para usar recalculate_sale_totals

### Tests
- `tests/unit/sales/test_services.py` — recalculate_sale_totals
- `tests/unit/pos/sales/test_discount.py`
- Actualizar tests existentes de items

### Migracion
`make migrations m="add tax_rate to products and sale_items add discount fields to sales"`

---

## Sesion 6: Venta Rapida (Quick Sale)

**Objetivo:** Operacion atomica de checkout completo en un solo request.

### Command
```python
@dataclass
class QuickSaleCommand(Command):
    items: list[dict]                # [{product_id, quantity, unit_price?, discount?}]
    payments: list[dict]             # [{amount, payment_method, reference?}]
    customer_id: int | None = None   # None = Consumidor Final (is_final_consumer=True)
    notes: str | None = None
```

### Handler (todo en una transaccion)
1. Obtener turno activo (obligatorio)
2. Determinar cliente: si `customer_id` es None, crear Sale con `is_final_consumer=True`
3. Crear Sale en DRAFT con shift_id
4. Crear SaleItems con tax_rate del producto, calcular totales
5. Validar stock para cada item
6. Confirmar venta (CONFIRMED)
7. Crear Payments, validar que cubren el total
8. Crear movimientos OUT + decrementar stock
9. Publicar `SaleConfirmed(source="pos")`
10. Retornar venta completa con items y pagos

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/sales/quick` | Checkout completo en un request |

### Validators
- `QuickSaleItemInput(productId, quantity, unitPrice?, discount?)`
- `QuickSalePaymentInput(amount, paymentMethod, reference?)`
- `QuickSaleRequest(customerId?, items[], payments[], notes?)`
- `QuickSaleResponse` — venta + items + pagos

### Archivos a crear/modificar
- `src/pos/sales/app/commands/quick_sale.py` — nuevo
- `src/pos/sales/infra/validators.py` — agregar validators
- `src/pos/sales/infra/routes.py` — agregar endpoint
- `src/pos/sales/infra/container.py` — registrar handler

### Tests
- `tests/unit/pos/sales/test_quick_sale.py` — happy path, stock insuficiente, pago incompleto, sin turno

### Dependencias: Sesiones 1 (turnos), 3 (consumidor final + turno en venta), 5 (impuestos)

---

## Sesion 7: Devoluciones y Reembolsos

**Objetivo:** Submodulo `pos/refund` para devoluciones parciales o totales con reposicion de inventario.

### Entidades
- `Refund`: `id`, `original_sale_id`, `shift_id`, `refund_date`, `subtotal`, `tax`, `total`, `reason`, `status: RefundStatus`, `refunded_by`
- `RefundItem`: `id`, `refund_id`, `original_sale_item_id`, `product_id`, `quantity`, `unit_price`, `tax_rate`, `tax_amount`, `discount`, `subtotal`
- `RefundPayment`: `id`, `refund_id`, `amount`, `payment_method`, `reference`
- `RefundStatus`: `PENDING`, `COMPLETED`, `CANCELLED`

### Estructura
```
src/pos/refund/
├── domain/
│   ├── entities.py     # Refund, RefundItem, RefundPayment, RefundStatus
│   ├── events.py       # RefundCompleted
│   └── exceptions.py   # ExceedsOriginalQuantityError, etc.
├── app/
│   ├── commands/
│   │   ├── create_refund.py
│   │   ├── process_refund.py   # Procesa pago + restock atomico
│   │   └── cancel_refund.py
│   └── queries/
│       └── get_refunds.py
└── infra/
    ├── models.py, mappers.py, repositories.py
    ├── validators.py, routes.py, container.py
```

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/refunds` | Crear devolucion (items a devolver) |
| POST | `/api/pos/refunds/{id}/process` | Procesar pago + completar devolucion |
| POST | `/api/pos/refunds/{id}/cancel` | Cancelar devolucion pendiente |
| GET | `/api/pos/refunds/{id}` | Obtener devolucion |
| GET | `/api/pos/refunds` | Listar devoluciones (filtro por saleId) |

### Flujo atomico de `process_refund`
1. Validar refund en PENDING
2. Crear RefundPayments
3. Marcar COMPLETED
4. Crear movimientos IN (restock)
5. Incrementar stock
6. Publicar `RefundCompleted`

### Tests
- `tests/unit/pos/refund/test_entities.py`
- `tests/unit/pos/refund/test_commands.py`

### Migracion
`make migrations m="create pos_refunds pos_refund_items pos_refund_payments tables"`

---

## Sesion 8: Movimientos de Caja + Reportes POS

**Objetivo:** Cash in/out dentro del turno y reportes operativos (X-Report, Z-Report, resumen diario).

### Movimientos de caja
- `CashMovement`: `id`, `shift_id`, `type: IN/OUT`, `amount`, `reason`, `performed_by`, `created_at`
- Command: `RegisterCashMovementCommand(shift_id, type, amount, reason)`
- Modificar `CloseShiftCommandHandler`: `expected = opening + cash_sales - cash_refunds + cash_in - cash_out`

### Estructura
```
src/pos/cash/
├── domain/entities.py
├── app/commands/register_cash_movement.py
├── app/queries/get_cash_movements.py
└── infra/models.py, mappers.py, repositories.py, validators.py, routes.py, container.py
```

### Reportes POS
- Queries en `src/pos/reports/` usando SQLAlchemy Session directamente (patron de `src/reports/inventory/`)
- **X-Report**: resumen de turno (ventas, pagos por metodo, items vendidos) — no cierra turno
- **Z-Report**: cierre de turno (X-Report + reconciliacion de caja, devoluciones)
- **Resumen diario**: ventas por fecha, desglose por metodo de pago, top productos

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/pos/shifts/{id}/cash-movements` | Registrar cash in/out |
| GET | `/api/pos/shifts/{id}/cash-movements` | Listar movimientos de caja |
| GET | `/api/pos/shifts/{id}/cash-summary` | Resumen de caja del turno |
| GET | `/api/pos/reports/x-report?shiftId=...` | X-Report |
| GET | `/api/pos/reports/z-report?shiftId=...` | Z-Report |
| GET | `/api/pos/reports/daily?date=...` | Resumen diario |
| GET | `/api/pos/reports/by-payment-method` | Ventas por metodo de pago |

### Tests
- `tests/unit/pos/cash/test_commands.py`
- `tests/unit/pos/reports/test_queries.py`

### Migracion
`make migrations m="create pos_cash_movements table"`

### Dependencias: Sesiones 1, 7 (datos de turnos y devoluciones)

---

## Sesion 9: Override de Precio + Generacion de Recibo

**Objetivo:** Permitir cambio de precio por item (con auditoria) y generar datos de recibo termico.

### Override de precio
- Agregar a `SaleItem`: `price_override: Decimal | None`, `override_reason: str | None`
- Command: `OverrideItemPriceCommand(sale_id, item_id, new_price, reason)`
- Recalcula totales de la venta

### Generacion de recibo
- Query: `GenerateReceiptQuery(sale_id)` -> datos estructurados del recibo
- Contenido: info empresa, fecha, cajero, items (cantidad, precio, IVA), subtotal, desglose IVA 12%/0%, descuentos, total, pagos, cambio
- El frontend renderiza para impresora termica

### Endpoints
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| PUT | `/api/pos/sales/{id}/items/{item_id}/price` | Override de precio |
| GET | `/api/pos/sales/{id}/receipt` | Obtener datos del recibo |

### Archivos a crear/modificar
- `src/sales/domain/entities.py` — agregar price_override a SaleItem
- `src/sales/infra/models.py` — agregar columnas
- `src/pos/sales/app/commands/override_price.py` — nuevo
- `src/pos/sales/app/queries/generate_receipt.py` — nuevo
- `src/pos/sales/infra/routes.py` — agregar endpoints

### Tests
- `tests/unit/pos/sales/test_override_price.py`
- `tests/unit/pos/sales/test_receipt.py`

### Migracion
`make migrations m="add price_override fields to sale_items"`

---

## Grafo de Dependencias

```
Sesion 1 (Turnos) ──────────┬── Sesion 3 (Vincular ventas a turno)
                             ├── Sesion 6 (Quick Sale requiere turno)
                             └── Sesion 8 (Cash + Reportes)

Sesion 2 (Busqueda + Cliente) ── Independiente

Sesion 3 (Update items + turno + CF) ── Requisito para Sesion 6

Sesion 4 (Park/Resume) ─────── Independiente

Sesion 5 (Descuentos + IVA) ┬── Sesion 6 (Quick Sale con impuestos)
                             ├── Sesion 7 (Refund con impuestos)
                             └── Sesion 9 (Recibo con desglose IVA)
```

**Orden recomendado de ejecucion:** 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9

Las sesiones 4 y 2 son relativamente independientes y pueden ejecutarse en cualquier orden despues de la 1.

---

## Resumen de Endpoints Totales

### Turnos (`/api/pos/shifts`)
- POST `/open` — Abrir turno
- POST `/{id}/close` — Cerrar turno
- GET `/active` — Turno activo
- GET `/{id}` — Obtener turno
- GET `/` — Listar turnos

### Productos (`/api/pos/products`)
- GET `/` — Listar (existente)
- GET `/{id}` — Obtener (existente)
- GET `/search?term=...` — Buscar por SKU/barcode/nombre

### Clientes (`/api/pos/customers`)
- GET `/` — Listar (existente)
- GET `/{id}` — Obtener (existente)
- GET `/search/by-tax-id` — Buscar por tax ID (existente)
- POST `/` — Crear rapido

### Ventas (`/api/pos/sales`)
- POST `/` — Crear (existente)
- POST `/quick` — Venta rapida
- GET `/{id}` — Obtener (existente)
- POST `/{id}/items` — Agregar item (existente)
- PUT `/{id}/items/{item_id}` — Actualizar item
- PUT `/{id}/items/{item_id}/price` — Override precio
- DELETE `/{id}/items/{item_id}` — Eliminar item (existente)
- POST `/{id}/confirm` — Confirmar (existente)
- POST `/{id}/cancel` — Cancelar (existente)
- POST `/{id}/park` — Aparcar
- POST `/{id}/resume` — Retomar
- GET `/parked` — Listar aparcadas
- POST `/{id}/discount` — Aplicar descuento
- POST `/{id}/payments` — Registrar pago (existente)
- GET `/{id}/payments` — Listar pagos (existente)
- GET `/{id}/receipt` — Generar recibo

### Devoluciones (`/api/pos/refunds`)
- POST `/` — Crear devolucion
- POST `/{id}/process` — Procesar
- POST `/{id}/cancel` — Cancelar
- GET `/{id}` — Obtener
- GET `/` — Listar

### Caja (`/api/pos/shifts/{id}/cash-*`)
- POST `/{id}/cash-movements` — Cash in/out
- GET `/{id}/cash-movements` — Listar movimientos
- GET `/{id}/cash-summary` — Resumen de caja

### Reportes (`/api/pos/reports`)
- GET `/x-report?shiftId=...` — X-Report
- GET `/z-report?shiftId=...` — Z-Report
- GET `/daily?date=...` — Resumen diario
- GET `/by-payment-method` — Por metodo de pago

---

## Archivos Clave de Referencia

| Archivo | Para que |
|---------|----------|
| `src/pos/sales/app/commands/confirm_sale.py` | Patron de operacion atomica POS |
| `src/sales/domain/entities.py` | Entidad Sale que se extiende en sesiones 3, 4, 5, 9 |
| `src/sales/infra/models.py` | Modelo Sale que requiere migraciones |
| `src/container.py` | Registrar INJECTABLES de cada nuevo submodulo |
| `main.py` | Registrar nuevos routers bajo pos_router |
| `src/reports/inventory/` | Patron para reportes POS (queries con Session directa) |

## Verificacion

Cada sesion debe verificarse con:
1. `make lint` — sin errores de formateo
2. `make tests` — todos los tests pasan (nuevos y existentes)
3. `make dev` — servidor arranca sin errores
4. Probar endpoints manualmente en `/docs/pos`
