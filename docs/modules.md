# Modulos de Dominio

## Catalogo

### Product

Gestion del catalogo de productos con categorias.

**Entidades:** `Category`, `Product`

**Campos clave de Product:**
- `id`, `sku`, `name`, `description`
- `category_id`, `uom_id`
- `price`, `cost`
- `is_active`, `created_at`

**Comandos:** `CreateCategory`, `UpdateCategory`, `DeleteCategory`, `CreateProduct`, `UpdateProduct`, `DeleteProduct`

**Queries:** `GetAllCategories`, `GetCategoryById`, `GetAllProducts`, `GetProductById`

**Eventos:** `ProductCreated`, `ProductUpdated`

---

### UoM (Unidades de Medida)

Registro de unidades de medida vinculadas a productos.

**Entidades:** `UnitOfMeasure`

**Campos:** `id`, `name`, `abbreviation`

**Comandos:** `CreateUnitOfMeasure`, `UpdateUnitOfMeasure`, `DeleteUnitOfMeasure`

**Queries:** `GetAllUnitsOfMeasure`, `GetUnitOfMeasureById`

---

## Inventario

### Warehouse

Instalaciones fisicas de almacenamiento.

**Entidades:** `Warehouse`

**Campos:** `id`, `name`, `address`, `is_active`

**Comandos:** `CreateWarehouse`, `UpdateWarehouse`, `DeleteWarehouse`

**Queries:** `GetAllWarehouses`, `GetWarehouseById`

---

### Location

Ubicaciones (estantes, zonas) dentro de un almacen.

**Entidades:** `Location`

**Campos:** `id`, `name`, `code`, `warehouse_id`, `is_active`

**Comandos:** `CreateLocation`, `UpdateLocation`, `DeleteLocation`

**Queries:** `GetAllLocations`, `GetLocationById`, `GetLocationsByWarehouse`

---

### Stock

Nivel de inventario de un producto en una ubicacion especifica. El stock no se gestiona directamente — se actualiza automaticamente mediante el evento `MovementCreated`.

**Entidades:** `Stock`

**Campos:** `id`, `product_id`, `location_id`, `quantity`, `min_quantity`, `updated_at`

**Queries:** `GetAllStock`, `GetStockById`, `GetStockByProduct`, `GetStockByLocation`

**Eventos recibidos:** `MovementCreated` → actualiza `quantity`

---

### Movement

Registro de entradas (`IN`) y salidas (`OUT`) de inventario. Cada movimiento genera el evento `MovementCreated`.

**Entidades:** `Movement`

**Campos:** `id`, `product_id`, `location_id`, `type` (IN/OUT), `quantity`, `reference`, `notes`, `created_at`

**Comandos:** `CreateMovement`

**Queries:** `GetAllMovements`, `GetMovementById`, `GetMovementsByProduct`

**Eventos publicados:** `MovementCreated`

**Origenes posibles de un Movement:**
- Confirmacion de venta → `SaleConfirmed` → OUT
- Anulacion de venta → `SaleCancelled` → IN
- Recepcion de compra → `PurchaseOrderReceived` → IN
- Ajuste de inventario → directo
- Creacion manual → via endpoint

---

### Lot

Trazabilidad por lote para productos perecederos o con fecha de vencimiento.

**Entidades:** `Lot`

**Campos:** `id`, `stock_id`, `lot_number`, `expiry_date`, `quantity`, `status`, `created_at`

**Comandos:** `CreateLot`, `UpdateLot`

**Queries:** `GetAllLots`, `GetLotById`, `GetLotsByStock`

**Eventos publicados:** `LotCreated`, `LotUpdated`

---

### Serial

Trazabilidad individual por numero de serie dentro de un lote.

**Entidades:** `Serial`

**Campos:** `id`, `lot_id`, `serial_number`, `status` (AVAILABLE/SOLD/RETURNED/DAMAGED), `created_at`

**Comandos:** `CreateSerial`, `UpdateSerial`

**Queries:** `GetAllSerials`, `GetSerialById`, `GetSerialsByLot`

---

### Adjustment

Ajustes de inventario para conteos fisicos, correcciones o bajas.

**Entidades:** `Adjustment`, `AdjustmentItem`

**Campos Adjustment:** `id`, `type` (COUNT/CORRECTION/WRITEOFF), `location_id`, `status`, `notes`, `created_at`

**Campos AdjustmentItem:** `id`, `adjustment_id`, `product_id`, `expected_qty`, `actual_qty`, `difference`

**Comandos:** `CreateAdjustment`, `UpdateAdjustment`, `CreateAdjustmentItem`, `UpdateAdjustmentItem`, `DeleteAdjustmentItem`

**Queries:** `GetAllAdjustments`, `GetAdjustmentById`, `GetAdjustmentItems`

---

### Transfer

Transferencias de stock entre ubicaciones.

**Entidades:** `Transfer`, `TransferItem`

**Campos Transfer:** `id`, `from_location_id`, `to_location_id`, `status`, `notes`, `created_at`

**Campos TransferItem:** `id`, `transfer_id`, `product_id`, `quantity`

**Comandos:** `CreateTransfer`, `UpdateTransfer`, `CreateTransferItem`, `UpdateTransferItem`, `DeleteTransferItem`

**Queries:** `GetAllTransfers`, `GetTransferById`, `GetTransferItems`

---

### Alert

Monitoreo de niveles de stock por debajo del minimo configurado.

**Entidades:** `Alert`

**Campos:** `id`, `stock_id`, `product_id`, `current_quantity`, `min_quantity`, `severity`, `created_at`

**Queries:** `GetAllAlerts`, `GetAlertById`, `GetAlertsByStock`, `GetAlertsByProduct`

> Las alertas se generan automaticamente cuando el stock cae por debajo del umbral minimo.

---

## Clientes

Gestion de clientes con datos fiscales, contactos y estados.

**Entidades:** `Customer`, `CustomerContact`

**Campos Customer:** `id`, `name`, `tax_id` (RUC/RUC), `tax_type`, `email`, `phone`, `address`, `is_active`, `created_at`

**Value Objects usados:** `TaxId`, `Email`

**Ciclo de vida:** activo / inactivo (activate/deactivate)

**Comandos:** `CreateCustomer`, `UpdateCustomer`, `DeleteCustomer`, `ActivateCustomer`, `DeactivateCustomer`, `CreateCustomerContact`, `UpdateCustomerContact`, `DeleteCustomerContact`

**Queries:** `GetAllCustomers`, `GetCustomerById`, `GetCustomerByTaxId`, `GetContactsByCustomer`

**Eventos:** `CustomerCreated`, `CustomerUpdated`, `CustomerActivated`, `CustomerDeactivated`

**Specifications:** `ActiveCustomers`, `CustomersByType`

---

## Proveedores

Gestion de proveedores con contactos y catalogo de productos que ofrecen.

**Entidades:** `Supplier`, `SupplierContact`, `SupplierProduct`

**Campos Supplier:** `id`, `name`, `tax_id`, `email`, `phone`, `address`, `is_active`

**Campos SupplierProduct:** `id`, `supplier_id`, `product_id`, `reference_code`, `unit_price`, `lead_time_days`

**Comandos:** `CreateSupplier`, `UpdateSupplier`, `DeleteSupplier`, `CreateSupplierContact`, `UpdateSupplierContact`, `DeleteSupplierContact`, `CreateSupplierProduct`, `UpdateSupplierProduct`, `DeleteSupplierProduct`

**Queries:** `GetAllSuppliers`, `GetSupplierById`, `GetContactsBySupplier`, `GetProductsBySupplier`

---

## Compras

Gestion de ordenes de compra y recepciones de mercaderia.

**Entidades:** `PurchaseOrder`, `PurchaseOrderItem`

**Estados de PO:** `DRAFT` → `CONFIRMED` → `RECEIVED` → `CANCELLED`

**Campos PurchaseOrder:** `id`, `supplier_id`, `status`, `notes`, `expected_date`, `created_at`

**Campos PurchaseOrderItem:** `id`, `purchase_order_id`, `product_id`, `quantity`, `unit_price`

**Comandos:** `CreatePurchaseOrder`, `AddPurchaseOrderItem`, `UpdatePurchaseOrderItem`, `DeletePurchaseOrderItem`, `ReceivePurchaseOrder`

**Queries:** `GetAllPurchaseOrders`, `GetPurchaseOrderById`, `GetPurchaseOrderItems`

**Eventos publicados:** `PurchaseOrderReceived`

**Integracion:** Al recepcionar (`ReceivePurchaseOrder`), se publica `PurchaseOrderReceived` → Inventory crea Movement(IN) por cada item → Stock se incrementa.

---

## Ventas

Ciclo de vida completo de ventas con items, pagos e integracion con inventario.

**Entidades:** `Sale`, `SaleItem`, `Payment`

**Estados:** `DRAFT` → `CONFIRMED` → `CANCELLED`

**Campos Sale:** `id`, `customer_id`, `status`, `subtotal`, `tax`, `total`, `notes`, `created_at`

**Campos SaleItem:** `id`, `sale_id`, `product_id`, `quantity`, `unit_price`, `subtotal`

**Campos Payment:** `id`, `sale_id`, `amount`, `method`, `reference`, `created_at`

**Comandos:** `CreateSale`, `AddSaleItem`, `RemoveSaleItem`, `ConfirmSale`, `CancelSale`, `RegisterPayment`

**Queries:** `GetAllSales`, `GetSaleById`, `GetSaleItems`, `GetSalePayments`

**Eventos publicados:** `SaleCreated`, `SaleConfirmed`, `SaleCancelled`

**Integracion con inventario:**
- `SaleConfirmed` → Movement(OUT) por cada item → Stock decrementado
- `SaleCancelled` → Movement(IN) por cada item → Stock restaurado

**Reglas de dominio:**
- Solo se pueden agregar items si la venta esta en estado `DRAFT`
- Solo se puede confirmar una venta `DRAFT` con al menos un item
- Solo se puede cancelar una venta `CONFIRMED` o `DRAFT`

---

## POS (Punto de Venta)

Operaciones atomicas del punto de venta. Confirma o anula ventas asegurando consistencia con el inventario en una sola transaccion.

**Modulo:** `src/pos/sales/`

**Comandos:** `POSConfirmSale`, `POSCancelSale`

**Diferencia con Admin:** Las operaciones POS son atomicas — verifican stock disponible y crean movimientos en la misma transaccion, evitando inconsistencias en entornos de alta concurrencia.

---

## Reportes

Consultas analiticas de inventario sin estado propio — leen datos de los modulos de inventario.

**Modulo:** `src/reports/inventory/`

**Queries disponibles:**
- `GetInventoryValuation` — valor total del inventario por producto/ubicacion
- `GetInventoryRotation` — frecuencia de rotacion por producto en un periodo
- `GetInventoryMovementsReport` — movimientos agrupados por tipo y periodo
- `GetInventorySummary` — resumen consolidado de stock, alertas y valuacion
