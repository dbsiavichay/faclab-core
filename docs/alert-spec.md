# Especificacion del Modulo de Alertas de Inventario

## Descripcion General

El modulo de Alertas de Inventario es un modulo **de solo lectura** que monitorea niveles de stock y vencimiento de lotes. No almacena datos propios ni modifica estado; agrega informacion de los modulos de Stock, Product y Lot para generar alertas en tiempo real.

---

## Enums

### AlertType

| Valor           | Descripcion                                           |
|-----------------|-------------------------------------------------------|
| `low_stock`     | Cantidad del producto <= `minStock` y > 0             |
| `out_of_stock`  | Cantidad del producto = 0                             |
| `reorder_point` | Cantidad del producto <= `reorderPoint` y > 0         |
| `expiring_soon` | Lote vence dentro de N dias y tiene cantidad > 0      |

---

## Entidades

### StockAlert (solo lectura, no persistida)

| Campo            | Tipo           | Descripcion                                        |
|------------------|----------------|----------------------------------------------------|
| `type`           | AlertType      | Tipo de alerta                                     |
| `productId`      | int            | ID del producto                                    |
| `productName`    | string         | Nombre del producto                                |
| `sku`            | string         | SKU del producto                                   |
| `currentQuantity`| int            | Cantidad actual en stock o lote                    |
| `threshold`      | int            | Umbral que dispara la alerta (`minStock`, `reorderPoint`, o 0) |
| `warehouseId`    | int \| null    | ID del almacen (null si no se filtro por almacen)  |
| `lotId`          | int \| null    | ID del lote (solo para `expiring_soon`)            |
| `daysToExpiry`   | int \| null    | Dias hasta vencimiento (solo para `expiring_soon`) |

> **Nota:** Esta entidad no se persiste en base de datos. Se construye dinamicamente cada vez que se consulta.

---

## Endpoints API

Base URL: `/api/admin`

| Metodo | Ruta                     | Descripcion                                          |
|--------|--------------------------|------------------------------------------------------|
| GET    | `/alerts/low-stock`      | Productos con stock <= minStock y > 0                |
| GET    | `/alerts/out-of-stock`   | Productos con stock = 0                              |
| GET    | `/alerts/reorder-point`  | Productos con stock <= reorderPoint y > 0            |
| GET    | `/alerts/expiring-lots`  | Lotes que vencen dentro de N dias con cantidad > 0   |

> **Nota:** Los productos de tipo servicio (`isService = true`) se excluyen de todas las alertas.

---

## Schemas de Request/Response

> Todos los campos usan **camelCase** en JSON.

### GET `/alerts/low-stock`

**Query params:**

| Param         | Tipo        | Default | Validacion | Descripcion            |
|---------------|-------------|---------|------------|------------------------|
| `warehouseId` | int \| null | null    | >= 1       | Filtrar por almacen    |

**Response:**

```json
{
  "data": [
    {
      "type": "low_stock",
      "productId": 5,
      "productName": "Filamento PLA",
      "sku": "FIL-PLA-001",
      "currentQuantity": 3,
      "threshold": 10,
      "warehouseId": 1,
      "lotId": null,
      "daysToExpiry": null
    }
  ]
}
```

### GET `/alerts/out-of-stock`

**Query params:**

| Param         | Tipo        | Default | Validacion | Descripcion            |
|---------------|-------------|---------|------------|------------------------|
| `warehouseId` | int \| null | null    | >= 1       | Filtrar por almacen    |

**Response:**

```json
{
  "data": [
    {
      "type": "out_of_stock",
      "productId": 12,
      "productName": "Resina UV",
      "sku": "RES-UV-001",
      "currentQuantity": 0,
      "threshold": 0,
      "warehouseId": 1,
      "lotId": null,
      "daysToExpiry": null
    }
  ]
}
```

### GET `/alerts/reorder-point`

**Query params:**

| Param         | Tipo        | Default | Validacion | Descripcion            |
|---------------|-------------|---------|------------|------------------------|
| `warehouseId` | int \| null | null    | >= 1       | Filtrar por almacen    |

**Response:**

```json
{
  "data": [
    {
      "type": "reorder_point",
      "productId": 8,
      "productName": "Tornillo M3",
      "sku": "TOR-M3-001",
      "currentQuantity": 15,
      "threshold": 20,
      "warehouseId": null,
      "lotId": null,
      "daysToExpiry": null
    }
  ]
}
```

### GET `/alerts/expiring-lots`

**Query params:**

| Param  | Tipo | Default | Validacion | Descripcion                            |
|--------|------|---------|------------|----------------------------------------|
| `days` | int  | 30      | >= 1       | Dias para considerar "proximo a vencer"|

**Response:**

```json
{
  "data": [
    {
      "type": "expiring_soon",
      "productId": 3,
      "productName": "Leche en polvo",
      "sku": "LEC-POL-001",
      "currentQuantity": 25,
      "threshold": 0,
      "warehouseId": null,
      "lotId": 7,
      "daysToExpiry": 12
    }
  ]
}
```

---

## StockAlertResponse (schema comun)

Todas las respuestas devuelven un array de objetos con este schema:

| Campo            | Tipo        | Presente en                                   |
|------------------|-------------|-----------------------------------------------|
| `type`           | string      | Todos                                         |
| `productId`      | int         | Todos                                         |
| `productName`    | string      | Todos                                         |
| `sku`            | string      | Todos                                         |
| `currentQuantity`| int         | Todos                                         |
| `threshold`      | int         | Todos (0 para out_of_stock y expiring_soon)   |
| `warehouseId`    | int \| null | low_stock, out_of_stock, reorder_point        |
| `lotId`          | int \| null | Solo expiring_soon                            |
| `daysToExpiry`   | int \| null | Solo expiring_soon                            |

---

## Reglas de Negocio

1. **low_stock**: Se activa cuando `currentQuantity <= product.minStock` y `currentQuantity > 0`. El `threshold` es el `minStock` del producto.
2. **out_of_stock**: Se activa cuando `currentQuantity = 0`. El `threshold` siempre es 0.
3. **reorder_point**: Se activa cuando `currentQuantity <= product.reorderPoint` y `currentQuantity > 0`. El `threshold` es el `reorderPoint` del producto.
4. **expiring_soon**: Se activa cuando un lote vence dentro de los proximos `days` dias y `currentQuantity > 0`. El `threshold` es 0. Incluye `lotId` y `daysToExpiry`.
5. Los productos marcados como **servicio** (`isService = true`) se excluyen de todas las alertas.
6. Si `warehouseId` se proporciona en low_stock, out_of_stock o reorder_point, solo se evaluan stocks de ese almacen.
7. Las alertas se calculan **en tiempo real** en cada consulta (no hay cache ni estado persistido).

---

## Errores

Este modulo no produce errores de negocio (no modifica estado). Los unicos errores posibles son de validacion:

| Codigo HTTP | Condicion                                    |
|-------------|----------------------------------------------|
| 422         | `warehouseId` menor a 1                      |
| 422         | `days` menor a 1                             |

Formato de error:

```json
{
  "errorCode": "VALIDATION_ERROR",
  "message": "Validation error",
  "timestamp": "2026-03-08T10:30:00",
  "requestId": "uuid",
  "detail": [
    {
      "loc": ["query", "warehouseId"],
      "msg": "Input should be greater than or equal to 1",
      "type": "value_error"
    }
  ]
}
```

---

## Dependencias con Otros Modulos

| Modulo    | Relacion                                                            |
|-----------|---------------------------------------------------------------------|
| Stock     | Se consulta para obtener cantidades actuales por producto/ubicacion  |
| Product   | Se consulta para obtener nombre, SKU, minStock, reorderPoint, isService |
| Lot       | Se consulta para obtener lotes proximos a vencer                    |
| Warehouse | `warehouseId` se usa como filtro opcional                           |

---

## Guia de Implementacion Frontend

### Vista Sugerida: Dashboard de Alertas (`/alerts`)

Panel con **4 secciones** o **tabs**, una por tipo de alerta:

#### 1. Stock Bajo (`low_stock`)
- Tabla con columnas: Producto, SKU, Cantidad Actual, Minimo, Almacen
- Badge amarillo/naranja
- Filtro por almacen (select, GET `/api/admin/warehouses`)

#### 2. Sin Stock (`out_of_stock`)
- Tabla con columnas: Producto, SKU, Almacen
- Badge rojo
- Filtro por almacen

#### 3. Punto de Reorden (`reorder_point`)
- Tabla con columnas: Producto, SKU, Cantidad Actual, Punto Reorden, Almacen
- Badge azul
- Filtro por almacen

#### 4. Lotes por Vencer (`expiring_soon`)
- Tabla con columnas: Producto, SKU, Lote, Cantidad, Dias para Vencer
- Badge naranja si > 7 dias, rojo si <= 7 dias
- Input numerico para dias (default 30)

### Componentes de Resumen

En un dashboard general o en la barra lateral, mostrar **contadores** con el total de alertas por tipo:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Stock Bajo  │  │  Sin Stock   │  │  Reorden     │  │  Por Vencer  │
│     12       │  │      3       │  │      8       │  │      5       │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

Para obtener los contadores, hacer las 4 llamadas y contar `data.length`.

### Flujo de Usuario Tipico

```
1. Abrir dashboard de alertas
2. Ver resumen de contadores por tipo
3. Seleccionar tab o seccion de interes
4. (Opcional) Filtrar por almacen o ajustar dias de vencimiento
5. Revisar productos/lotes en alerta
6. Tomar accion: crear orden de compra, hacer ajuste, o transferencia
```

### Consideraciones de UX

- Las alertas son de **solo lectura**: no hay acciones de crear/editar/eliminar
- Refrescar datos periodicamente o con boton de recarga (son calculadas en tiempo real)
- Enlazar productos a su detalle (`/products/{productId}`)
- Enlazar lotes a su detalle cuando aplique (`/lots/{lotId}`)
- Mostrar estado vacio ("Sin alertas") cuando el array `data` este vacio
- No hay paginacion; las respuestas retornan todos los resultados
- Considerar agrupar alertas por almacen si hay multiples almacenes
