# Warehouse API - Especificación para Implementación Frontend

## Información General

**Base URL:** `http://localhost:3000`

**Tecnología:** FastAPI con soporte completo de OpenAPI/Swagger

**Documentación Interactiva:** `http://localhost:3000/docs`

**CORS:** Configurado para permitir requests desde `http://localhost:3000` y `http://localhost:5173`

**Content-Type:** `application/json`

---

## Arquitectura de Respuestas

### Respuestas Exitosas
Las respuestas exitosas siguen el formato JSON estándar según el endpoint.

### Respuestas de Error
El API utiliza un middleware de manejo de errores que devuelve respuestas consistentes:

```json
{
  "detail": "Mensaje de error descriptivo"
}
```

**Códigos de Estado HTTP:**
- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `204 No Content` - Operación exitosa sin contenido (deletes)
- `400 Bad Request` - Error de validación o datos inválidos
- `404 Not Found` - Recurso no encontrado
- `422 Unprocessable Entity` - Error de validación de Pydantic
- `500 Internal Server Error` - Error interno del servidor

---

## 1. Módulo de Categorías

### Endpoints

#### 1.1. Crear Categoría
```http
POST /categories
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string"  // opcional
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "description": "string"
}
```

---

#### 1.2. Actualizar Categoría
```http
PUT /categories/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID de la categoría

**Request Body:**
```json
{
  "name": "string",
  "description": "string"  // opcional
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "description": "string"
}
```

---

#### 1.3. Eliminar Categoría
```http
DELETE /categories/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID de la categoría

**Response:** `204 No Content`

---

#### 1.4. Obtener Todas las Categorías
```http
GET /categories
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "string",
    "description": "string"
  }
]
```

---

#### 1.5. Obtener Categoría por ID
```http
GET /categories/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID de la categoría

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "description": "string"
}
```

---

## 2. Módulo de Productos

### Endpoints

#### 2.1. Crear Producto
```http
POST /products
```

**Request Body:**
```json
{
  "name": "string",
  "sku": "string",
  "description": "string",  // opcional
  "categoryId": 1  // opcional, debe ser >= 1
}
```

**Nota:** El campo `categoryId` acepta tanto `categoryId` como `category_id` en el request.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "sku": "string",
  "description": "string",
  "categoryId": 1
}
```

---

#### 2.2. Actualizar Producto
```http
PUT /products/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del producto

**Request Body:**
```json
{
  "name": "string",
  "sku": "string",
  "description": "string",  // opcional
  "categoryId": 1  // opcional
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "sku": "string",
  "description": "string",
  "categoryId": 1
}
```

---

#### 2.3. Eliminar Producto
```http
DELETE /products/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del producto

**Response:** `204 No Content`

---

#### 2.4. Obtener Todos los Productos
```http
GET /products
```

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "sku": "string",
      "description": "string",
      "categoryId": 1
    }
  ]
}
```

---

#### 2.5. Obtener Producto por ID
```http
GET /products/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del producto

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "sku": "string",
  "description": "string",
  "categoryId": 1
}
```

---

## 3. Módulo de Stock

### Endpoints

#### 3.1. Obtener Stocks
```http
GET /stock
```

**Query Parameters:**
- `productId` (integer, optional) - Filtrar por ID de producto (>= 1)
- `limit` (integer, optional, default: 100) - Límite de resultados (1-1000)
- `offset` (integer, optional, default: 0) - Desplazamiento para paginación (>= 0)

**Ejemplo:**
```http
GET /stock?productId=5&limit=50&offset=0
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "productId": 1,
    "quantity": 100,
    "location": "string"  // puede ser null
  }
]
```

**Nota:** El campo `location` es opcional y puede ser `null`.

---

## 4. Módulo de Movimientos

### Tipos de Movimiento

**MovementType (enum):**
- `"in"` - Entrada de inventario (cantidad positiva)
- `"out"` - Salida de inventario (cantidad negativa)

### Endpoints

#### 4.1. Crear Movimiento
```http
POST /movements
```

**Request Body:**
```json
{
  "productId": 1,  // requerido, >= 1
  "quantity": 10,  // requerido, >= 1
  "type": "in",  // requerido: "in" | "out"
  "reason": "string",  // opcional
  "date": "2024-01-15T10:30:00"  // opcional, ISO 8601 datetime
}
```

**Validaciones Importantes:**
- Si `type` es `"in"`, la cantidad debe ser positiva
- Si `type` es `"out"`, la cantidad debe ser negativa
- La cantidad no puede ser cero

**Response:** `200 OK`
```json
{
  "id": 1,
  "productId": 1,
  "quantity": 10,
  "type": "in",
  "reason": "string",
  "date": "2024-01-15T10:30:00"
}
```

---

#### 4.2. Obtener Movimientos
```http
GET /movements
```

**Query Parameters:**
- `productId` (integer, optional) - Filtrar por ID de producto (>= 1)
- `type` (string, optional) - Filtrar por tipo: `"in"` o `"out"`
- `fromDate` (datetime, optional) - Fecha inicio (ISO 8601)
- `toDate` (datetime, optional) - Fecha fin (ISO 8601)
- `limit` (integer, optional, default: 100) - Límite de resultados (1-1000)
- `offset` (integer, optional, default: 0) - Desplazamiento (>= 0)

**Ejemplo:**
```http
GET /movements?productId=5&type=in&fromDate=2024-01-01T00:00:00&toDate=2024-01-31T23:59:59&limit=50
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "productId": 1,
    "quantity": 10,
    "type": "in",
    "reason": "string",
    "date": "2024-01-15T10:30:00"
  }
]
```

---

## 5. Módulo de Clientes (Customers)

### Tipos de Identificación Fiscal

**TaxType (valores numéricos):**
- `1` - RUC
- `2` - NATIONAL_ID (Cédula)
- `3` - PASSPORT (Pasaporte)
- `4` - FOREIGN_ID (ID Extranjero)

### Endpoints

#### 5.1. Crear Cliente
```http
POST /customers
```

**Request Body:**
```json
{
  "name": "string",  // requerido, 1-128 caracteres
  "taxId": "string",  // requerido, 1-32 caracteres
  "taxType": 1,  // requerido, 1-4
  "email": "string",  // opcional, max 128 caracteres
  "phone": "string",  // opcional, max 32 caracteres
  "address": "string",  // opcional, max 255 caracteres
  "city": "string",  // opcional, max 64 caracteres
  "state": "string",  // opcional, max 64 caracteres
  "country": "string",  // opcional, max 64 caracteres
  "creditLimit": 0,  // opcional, decimal >= 0
  "paymentTerms": 30,  // opcional, entero >= 0 (días)
  "isActive": true  // opcional, default: true
}
```

**Nota:** Los campos aceptan tanto camelCase como snake_case.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "taxId": "string",
  "taxType": 1,
  "email": "string",
  "phone": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "country": "string",
  "creditLimit": 0,
  "paymentTerms": 30,
  "isActive": true
}
```

---

#### 5.2. Actualizar Cliente
```http
PUT /customers/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del cliente

**Request Body:** Mismo formato que crear cliente

**Response:** `200 OK` - Mismo formato que la respuesta de creación

---

#### 5.3. Eliminar Cliente
```http
DELETE /customers/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del cliente

**Response:** `204 No Content`

---

#### 5.4. Obtener Todos los Clientes
```http
GET /customers
```

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "name": "string",
      "taxId": "string",
      "taxType": 1,
      "email": "string",
      "phone": "string",
      "address": "string",
      "city": "string",
      "state": "string",
      "country": "string",
      "creditLimit": 0,
      "paymentTerms": 30,
      "isActive": true
    }
  ]
}
```

---

#### 5.5. Obtener Cliente por ID
```http
GET /customers/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del cliente

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "taxId": "string",
  "taxType": 1,
  "email": "string",
  "phone": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "country": "string",
  "creditLimit": 0,
  "paymentTerms": 30,
  "isActive": true
}
```

---

#### 5.6. Buscar Cliente por Tax ID
```http
GET /customers/search/by-tax-id?tax_id={taxId}
```

**Query Parameters:**
- `tax_id` (string, required) - ID fiscal del cliente

**Ejemplo:**
```http
GET /customers/search/by-tax-id?tax_id=1234567890
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "taxId": "1234567890",
  "taxType": 1,
  "email": "string",
  "phone": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "country": "string",
  "creditLimit": 0,
  "paymentTerms": 30,
  "isActive": true
}
```

---

#### 5.7. Activar Cliente
```http
POST /customers/{id}/activate
```

**Path Parameters:**
- `id` (integer, required) - ID del cliente

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "taxId": "string",
  "taxType": 1,
  "email": "string",
  "phone": "string",
  "address": "string",
  "city": "string",
  "state": "string",
  "country": "string",
  "creditLimit": 0,
  "paymentTerms": 30,
  "isActive": true
}
```

---

#### 5.8. Desactivar Cliente
```http
POST /customers/{id}/deactivate
```

**Path Parameters:**
- `id` (integer, required) - ID del cliente

**Response:** `200 OK` - Cliente con `isActive: false`

---

#### 5.9. Crear Contacto de Cliente
```http
POST /customers/{customer_id}/contacts
```

**Path Parameters:**
- `customer_id` (integer, required) - ID del cliente

**Request Body:**
```json
{
  "name": "string",  // requerido, 1-128 caracteres
  "role": "string",  // opcional, max 64 caracteres
  "email": "string",  // opcional, max 128 caracteres
  "phone": "string"  // opcional, max 32 caracteres
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "customerId": 1,
  "name": "string",
  "role": "string",
  "email": "string",
  "phone": "string"
}
```

---

#### 5.10. Obtener Contactos de Cliente
```http
GET /customers/{customer_id}/contacts
```

**Path Parameters:**
- `customer_id` (integer, required) - ID del cliente

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "customerId": 1,
      "name": "string",
      "role": "string",
      "email": "string",
      "phone": "string"
    }
  ]
}
```

---

## 6. Módulo de Contactos de Clientes

### Endpoints

#### 6.1. Actualizar Contacto
```http
PUT /customer-contacts/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del contacto

**Request Body:**
```json
{
  "name": "string",  // requerido, 1-128 caracteres
  "role": "string",  // opcional, max 64 caracteres
  "email": "string",  // opcional, max 128 caracteres
  "phone": "string"  // opcional, max 32 caracteres
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "customerId": 1,
  "name": "string",
  "role": "string",
  "email": "string",
  "phone": "string"
}
```

---

#### 6.2. Eliminar Contacto
```http
DELETE /customer-contacts/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del contacto

**Response:** `204 No Content`

---

#### 6.3. Obtener Contacto por ID
```http
GET /customer-contacts/{id}
```

**Path Parameters:**
- `id` (integer, required) - ID del contacto

**Response:** `200 OK`
```json
{
  "id": 1,
  "customerId": 1,
  "name": "string",
  "role": "string",
  "email": "string",
  "phone": "string"
}
```

---

## Modelos TypeScript de Referencia

### Category
```typescript
interface Category {
  id: number;
  name: string;
  description?: string | null;
}

interface CategoryInput {
  name: string;
  description?: string;
}
```

### Product
```typescript
interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string | null;
  categoryId?: number | null;
}

interface ProductInput {
  name: string;
  sku: string;
  description?: string;
  categoryId?: number;
}

interface ProductsResponse {
  data: Product[];
}
```

### Stock
```typescript
interface Stock {
  id: number;
  productId: number;
  quantity: number;
  location?: string | null;
}

interface StockQueryParams {
  productId?: number;
  limit?: number;  // default: 100, range: 1-1000
  offset?: number; // default: 0
}
```

### Movement
```typescript
type MovementType = "in" | "out";

interface Movement {
  id: number;
  productId: number;
  quantity: number;
  type: MovementType;
  reason?: string | null;
  date?: string | null;  // ISO 8601 datetime
}

interface MovementInput {
  productId: number;
  quantity: number;
  type: MovementType;
  reason?: string;
  date?: string;  // ISO 8601 datetime
}

interface MovementQueryParams {
  productId?: number;
  type?: MovementType;
  fromDate?: string;  // ISO 8601 datetime
  toDate?: string;    // ISO 8601 datetime
  limit?: number;     // default: 100, range: 1-1000
  offset?: number;    // default: 0
}
```

### Customer
```typescript
type TaxType = 1 | 2 | 3 | 4; // 1=RUC, 2=NATIONAL_ID, 3=PASSPORT, 4=FOREIGN_ID

interface Customer {
  id: number;
  name: string;
  taxId: string;
  taxType: TaxType;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  creditLimit?: number | null;
  paymentTerms?: number | null;
  isActive: boolean;
}

interface CustomerInput {
  name: string;
  taxId: string;
  taxType: TaxType;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  creditLimit?: number;
  paymentTerms?: number;
  isActive?: boolean;
}

interface CustomersResponse {
  data: Customer[];
}
```

### CustomerContact
```typescript
interface CustomerContact {
  id: number;
  customerId: number;
  name: string;
  role?: string | null;
  email?: string | null;
  phone?: string | null;
}

interface CustomerContactInput {
  name: string;
  role?: string;
  email?: string;
  phone?: string;
}

interface CustomerContactsResponse {
  data: CustomerContact[];
}
```

### Error Response
```typescript
interface ErrorResponse {
  detail: string;
}
```

---

## Consideraciones de Implementación

### 1. Manejo de Errores
Implementar un interceptor/middleware que capture errores HTTP y muestre mensajes apropiados al usuario:

```typescript
// Ejemplo con Axios
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.data?.detail) {
      // Mostrar error del API
      showError(error.response.data.detail);
    } else {
      // Mostrar error genérico
      showError('Ocurrió un error inesperado');
    }
    return Promise.reject(error);
  }
);
```

### 2. Formateo de Fechas
Las fechas deben enviarse en formato ISO 8601:
```typescript
const date = new Date();
const isoDate = date.toISOString(); // "2024-01-15T10:30:00.000Z"
```

### 3. Paginación
Implementar paginación para listados usando `limit` y `offset`:
```typescript
const page = 1;
const pageSize = 50;
const offset = (page - 1) * pageSize;

fetch(`/stock?limit=${pageSize}&offset=${offset}`)
```

### 4. Validación de Movimientos
Antes de enviar un movimiento, validar:
- Si es `type: "in"`, `quantity` debe ser positivo
- Si es `type: "out"`, `quantity` debe ser negativo
- Nunca enviar `quantity: 0`

```typescript
function validateMovement(movement: MovementInput): boolean {
  if (movement.quantity === 0) return false;
  if (movement.type === 'in' && movement.quantity < 0) return false;
  if (movement.type === 'out' && movement.quantity > 0) return false;
  return true;
}
```

### 5. Campos Opcionales vs Null
Los campos opcionales pueden ser:
- Omitidos del request body
- Enviados como `null`
- Enviados con un valor

En las responses, los campos opcionales sin valor aparecerán como `null`.

### 6. Case Sensitivity
El API acepta tanto camelCase como snake_case en los requests, pero siempre responde en camelCase. Es recomendable usar camelCase consistentemente en el frontend.

### 7. CORS
Asegurarse de que el frontend corra en uno de los orígenes permitidos:
- `http://localhost:3000`
- `http://localhost:5173`

### 8. Autenticación
Actualmente el API no tiene autenticación implementada. Si se agrega en el futuro, probablemente usará JWT tokens que deberán incluirse en el header `Authorization: Bearer {token}`.

---

## Ejemplos de Uso con Fetch API

### Crear un Producto
```typescript
async function createProduct(product: ProductInput): Promise<Product> {
  const response = await fetch('http://localhost:3000/products', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error creating product');
  }

  return response.json();
}
```

### Obtener Productos con Paginación
```typescript
async function getProducts(page: number = 1, pageSize: number = 50): Promise<ProductsResponse> {
  const offset = (page - 1) * pageSize;
  const response = await fetch(
    `http://localhost:3000/products?limit=${pageSize}&offset=${offset}`
  );

  if (!response.ok) {
    throw new Error('Error fetching products');
  }

  return response.json();
}
```

### Filtrar Movimientos
```typescript
async function getMovements(filters: MovementQueryParams): Promise<Movement[]> {
  const params = new URLSearchParams();

  if (filters.productId) params.append('productId', filters.productId.toString());
  if (filters.type) params.append('type', filters.type);
  if (filters.fromDate) params.append('fromDate', filters.fromDate);
  if (filters.toDate) params.append('toDate', filters.toDate);
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.offset) params.append('offset', filters.offset.toString());

  const response = await fetch(`http://localhost:3000/movements?${params}`);

  if (!response.ok) {
    throw new Error('Error fetching movements');
  }

  return response.json();
}
```

### Activar/Desactivar Cliente
```typescript
async function toggleCustomerStatus(customerId: number, activate: boolean): Promise<Customer> {
  const endpoint = activate ? 'activate' : 'deactivate';
  const response = await fetch(
    `http://localhost:3000/customers/${customerId}/${endpoint}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error updating customer status');
  }

  return response.json();
}
```

---

## Testing

Para probar el API:
1. Iniciar el servidor: `make dev`
2. Acceder a la documentación interactiva: `http://localhost:3000/docs`
3. Usar Swagger UI para probar endpoints directamente

También puedes usar herramientas como:
- Postman
- Insomnia
- curl
- Thunder Client (VS Code extension)

---

## Changelog y Versionado

**Versión Actual:** 1.0.0

El API no tiene versionado explícito en las URLs. Los cambios breaking se comunicarán mediante actualizaciones de este documento.

---

## Soporte y Contacto

Para reportar issues o solicitar features, revisar el repositorio del proyecto y el archivo ROADMAP.md.
