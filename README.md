# Faclab Core - Sistema de Ventas e Inventarios

Un sistema completo de ventas e inventarios construido con **FastAPI**, **Clean Architecture** y **CQRS**. Proporciona funcionalidad integral para gestionar el ciclo de ventas, desde el catalogo de productos hasta el control de inventarios, administracion de clientes y procesamiento de ventas.

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Framework | FastAPI 0.115 |
| Lenguaje | Python 3.12 |
| Base de Datos | PostgreSQL 14 |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic 1.15 |
| Servidor ASGI | Uvicorn |
| Inyeccion de Dependencias | wireup 2.7 |
| Observabilidad | OpenTelemetry (traces, metrics, logs) |
| Logging estructurado | structlog |
| Contenedores | Docker & Docker Compose |
| Testing | pytest + pytest-cov + pytest-mock |
| Linter/Formatter | ruff |

## Arquitectura

El proyecto sigue **Clean Architecture** con separacion estricta en tres capas, combinada con **CQRS** (Command Query Responsibility Segregation) para separar operaciones de lectura y escritura.

### Capas

```
Domain Layer    Entidades, Value Objects, Domain Events, Specifications
      |
Application     Commands, Queries, Handlers, Repository interfaces
      |
Infrastructure  Controllers, Routes, SQLAlchemy Models, Mappers, Repositories
```

### Estructura del Proyecto

```
faclab-core/
├── src/
│   ├── shared/                     # Infraestructura compartida y primitivas de dominio
│   │   ├── domain/                 # Entity base, Value Objects, Events, Specifications, Exceptions
│   │   ├── app/                    # Command/Query base, Repository interface
│   │   └── infra/                  # DB session, BaseRepository, Mappers, Middleware, EventBus, Telemetry
│   ├── catalog/
│   │   └── product/                # Productos y categorias
│   ├── inventory/
│   │   ├── stock/                  # Niveles de stock por producto
│   │   └── movement/               # Movimientos de inventario (entradas/salidas)
│   ├── customers/                  # Gestion de clientes y contactos
│   └── sales/                      # Ventas, items y pagos
├── config/                         # Configuracion por entorno (local, staging, production)
├── alembic/                        # Migraciones de base de datos
├── tests/                          # Tests unitarios e integracion
├── main.py                         # Punto de entrada
└── Makefile                        # Comandos de desarrollo
```

Cada modulo de dominio sigue la misma estructura interna:

```
modulo/
├── domain/
│   ├── entities.py                 # Entidades (dataclasses)
│   ├── events.py                   # Eventos de dominio
│   ├── specifications.py           # Especificaciones para consultas
│   └── exceptions.py               # Excepciones de dominio
├── app/
│   ├── commands/                   # Handlers de escritura (Create, Update, Delete)
│   ├── queries/                    # Handlers de lectura (GetAll, GetById, Search)
│   └── types.py                    # TypedDicts para entrada/salida
└── infra/
    ├── controllers.py              # Controladores HTTP
    ├── routes.py                   # Rutas FastAPI
    ├── validators.py               # Esquemas Pydantic
    ├── models.py                   # Modelos SQLAlchemy
    ├── mappers.py                  # Conversion Entity <-> Model
    └── repositories.py             # Implementacion de repositorios
```

## Patrones de Diseno

### CQRS (Command Query Responsibility Segregation)

Las operaciones de escritura y lectura estan separadas en handlers independientes:

- **Commands**: Operaciones que modifican estado (`CreateCustomerCommand`, `ConfirmSaleCommand`)
- **Queries**: Operaciones de solo lectura (`GetAllProductsQuery`, `GetSaleByIdQuery`)
- Cada handler recibe un dataclass tipado y retorna un resultado tipado

### Repository Pattern

`BaseRepository[E]` proporciona operaciones CRUD genericas. Los repositorios especificos heredan de este e implementan el atributo `__model__` para vincular con el modelo SQLAlchemy.

### Domain Events

Comunicacion desacoplada entre modulos mediante eventos de dominio:
- `SaleConfirmed` -> Inventory crea movimientos OUT automaticamente
- `SaleCancelled` -> Inventory revierte movimientos con entradas IN
- `MovementCreated` -> Stock actualiza cantidades

Los eventos se publican via `EventBus` y los handlers se registran con el decorador `@event_handler()`.

### Specification Pattern

Consultas complejas reutilizables y componibles con operadores `&` (AND), `|` (OR) y `~` (NOT):

```python
spec = ActiveCustomers() & CustomersByType("WHOLESALE")
customers = customer_repo.filter_by_spec(spec)
```

### Value Objects

Dataclasses inmutables (`frozen=True`) que encapsulan validacion:
- `Email` - Validacion de formato
- `TaxId` - Validacion de RUC (Ecuador)
- `Money` - Operaciones aritmeticas con moneda
- `Percentage` - Precision decimal para porcentajes

### Mapper Pattern

Conversion bidireccional entre entidades de dominio y modelos SQLAlchemy. Registrados como `SINGLETON` por ser stateless.

### Inyeccion de Dependencias

El contenedor DI (wireup) gestiona el ciclo de vida de los componentes:
- **SINGLETON**: Mappers (stateless, compartidos)
- **SCOPED**: Repositorios, handlers, controladores, sesiones DB (por peticion)
- **TRANSIENT**: Nueva instancia por resolucion

## Flujo de Datos

### Peticion HTTP

```
HTTP Request
    -> FastAPI Router
    -> ErrorHandlingMiddleware
    -> Controller (inyectado via wireup)
    -> CommandHandler / QueryHandler
        -> OpenTelemetry span + metricas
        -> Logica de negocio
        -> Repository -> Mapper -> SQLAlchemy -> PostgreSQL
        -> Publicar DomainEvents (si aplica)
    -> Event Handlers (en scope separado)
        -> Efectos secundarios (crear movimientos, actualizar stock)
    -> HTTP Response (JSON)
```

### Flujo de Venta

```
1. POST /sales              -> Crear venta (DRAFT)
2. POST /sales/{id}/items   -> Agregar items
3. POST /sales/{id}/confirm -> Confirmar venta
   -> Valida stock disponible
   -> Publica SaleConfirmed
   -> Inventory crea Movement(OUT) por cada item
   -> Stock se reduce automaticamente
4. POST /sales/{id}/payments -> Registrar pagos
5. POST /sales/{id}/cancel   -> Anular (si no facturada)
   -> Publica SaleCancelled
   -> Inventory crea Movement(IN) para revertir
   -> Stock se restaura
```

## Observabilidad

El sistema esta instrumentado con **OpenTelemetry**:

- **Traces**: Cada request HTTP y ejecucion de handler genera spans
- **Metrics**: Histogramas de duracion, contadores de invocaciones y errores
- **Logs**: structlog con formato JSON (produccion) o consola (desarrollo)
- **Exportacion**: OTLP gRPC hacia un collector configurable

## Manejo de Errores

Middleware centralizado con respuestas estructuradas:

| Tipo | HTTP Status | Uso |
|---|---|---|
| `DomainError` | 400 | Violaciones de reglas de negocio |
| `ApplicationError` | 400 | Errores de logica de aplicacion |
| `NotFoundError` | 404 | Recurso no encontrado |
| `ValidationError` | 422 | Validacion de entrada |

Formato de respuesta:
```json
{
  "error_code": "NOT_FOUND",
  "message": "Entity with id 1 not found",
  "timestamp": "2026-02-13T10:00:00Z",
  "request_id": "uuid",
  "detail": "contexto adicional"
}
```

## Requisitos Previos

- Docker y Docker Compose (recomendado)
- Python 3.11+ (para desarrollo local)
- PostgreSQL 14 (si se ejecuta sin Docker)

## Instalacion

1. Clonar el repositorio:
```bash
git clone https://github.com/Faclab/faclab-core.git
cd faclab-core
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con las credenciales de base de datos
```

Variables requeridas:
```
DB_CONNECTION_STRING=postgresql://user:password@localhost:5432/faclab_db
ENVIRONMENT=local
```

## Ejecucion

### Docker (Recomendado)

```bash
make dev     # Servidor de desarrollo con hot-reload en http://localhost:3000
```

La API redirige automaticamente a la documentacion Swagger en `/docs`.

### Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Comandos de Desarrollo

```bash
# Docker
make build                      # Construir imagenes
make start                      # Iniciar contenedores (detached)
make dev                        # Desarrollo con hot-reload
make down                       # Detener contenedores

# Base de datos
make migrations m="descripcion" # Crear migracion
make upgrade                    # Aplicar migraciones
make downgrade d=revision_id    # Revertir migracion

# Testing y calidad
make tests                      # Tests con cobertura (Docker)
make lint                       # Formatear y validar codigo (ruff)
```

## API Endpoints

### Catalogo

| Metodo | Ruta | Descripcion |
|---|---|---|
| `POST` | `/categories` | Crear categoria |
| `GET` | `/categories` | Listar categorias |
| `GET` | `/categories/{id}` | Obtener por ID |
| `PUT` | `/categories/{id}` | Actualizar |
| `DELETE` | `/categories/{id}` | Eliminar |
| `POST` | `/products` | Crear producto |
| `GET` | `/products` | Listar con paginacion |
| `GET` | `/products/{id}` | Obtener por ID |
| `PUT` | `/products/{id}` | Actualizar |
| `DELETE` | `/products/{id}` | Eliminar |
| `GET` | `/products/search` | Buscar por nombre/SKU |

### Inventario

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/stock` | Listar stock |
| `GET` | `/stock/{id}` | Obtener por ID |
| `GET` | `/stock/product/{product_id}` | Stock por producto |
| `POST` | `/movements` | Crear movimiento (IN/OUT) |
| `GET` | `/movements` | Listar movimientos |
| `GET` | `/movements/{id}` | Obtener por ID |

### Clientes

| Metodo | Ruta | Descripcion |
|---|---|---|
| `POST` | `/customers` | Crear cliente |
| `GET` | `/customers` | Listar clientes |
| `GET` | `/customers/{id}` | Obtener por ID |
| `GET` | `/customers/tax-id/{tax_id}` | Buscar por RUC |
| `PUT` | `/customers/{id}` | Actualizar |
| `DELETE` | `/customers/{id}` | Eliminar |
| `POST` | `/customers/{id}/activate` | Activar |
| `POST` | `/customers/{id}/deactivate` | Desactivar |

### Contactos de Clientes

| Metodo | Ruta | Descripcion |
|---|---|---|
| `POST` | `/customer-contacts` | Crear contacto |
| `GET` | `/customer-contacts/{id}` | Obtener por ID |
| `PUT` | `/customer-contacts/{id}` | Actualizar |
| `DELETE` | `/customer-contacts/{id}` | Eliminar |
| `GET` | `/customer-contacts/customer/{id}` | Contactos por cliente |

### Ventas

| Metodo | Ruta | Descripcion |
|---|---|---|
| `POST` | `/sales` | Crear venta (DRAFT) |
| `GET` | `/sales` | Listar ventas |
| `GET` | `/sales/{id}` | Obtener por ID |
| `POST` | `/sales/{id}/items` | Agregar item |
| `DELETE` | `/sales/{id}/items/{item_id}` | Remover item |
| `POST` | `/sales/{id}/confirm` | Confirmar venta |
| `POST` | `/sales/{id}/cancel` | Anular venta |
| `POST` | `/sales/{id}/payments` | Registrar pago |
| `GET` | `/sales/{id}/payments` | Listar pagos |
| `GET` | `/sales/{id}/items` | Listar items |

### Documentacion Interactiva

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Configuracion

La aplicacion soporta multiples entornos via archivos en `config/`:

| Archivo | Entorno |
|---|---|
| `config/local.py` | Desarrollo local |
| `config/staging.py` | Staging |
| `config/production.py` | Produccion |

Se selecciona con la variable `ENVIRONMENT` (default: `local`).

Configuraciones disponibles: conexion a DB, nivel de logs, OpenTelemetry (endpoint OTLP, service name, sampling rate).

## Testing

```bash
# Ejecutar todos los tests con cobertura
make tests

# Ejecucion local
.venv/bin/python -m pytest tests/ -v

# Solo tests unitarios
.venv/bin/python -m pytest tests/unit/ -v

# Solo tests de integracion
.venv/bin/python -m pytest tests/integration/ -v
```

La suite incluye:
- **Tests unitarios**: Entidades, value objects, specifications, commands, queries, event handlers
- **Tests de integracion**: Flujos cross-module (Movement -> Stock, Sale -> Movement -> Stock)
- **Fixtures**: Factory functions para entidades, `clear_event_bus` para aislamiento

## Guia de Contribucion

### Configurar entorno de desarrollo

```bash
git clone https://github.com/Faclab/faclab-core.git
cd faclab-core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements_dev.txt
```

### Convenciones de codigo

- **Formatter/Linter**: ruff (ejecutar `make lint` antes de commitear)
- **Entidades de dominio**: Dataclasses inmutables que extienden `Entity`
- **Modelos SQLAlchemy**: Solo en la capa de infraestructura (`infra/models.py`)
- **Dependencia entre capas**: Domain <- Application <- Infrastructure (nunca al reves)
- **Commits**: Usar [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`)

### Agregar un nuevo modulo

1. Crear estructura de directorios:
   ```
   src/nuevo_modulo/
   ├── domain/
   │   ├── entities.py          # Dataclass(Entity)
   │   ├── events.py            # DomainEvent subclasses
   │   └── specifications.py    # Specification subclasses
   ├── app/
   │   ├── commands/             # CommandHandler[TCmd, TResult]
   │   ├── queries/              # QueryHandler[TQuery, TResult]
   │   └── types.py              # TypedDicts de entrada/salida
   └── infra/
       ├── models.py             # SQLAlchemy Model(Base)
       ├── mappers.py            # Mapper[Entity, Model]
       ├── repositories.py       # Repository factories
       ├── controllers.py        # Controller con wireup injection
       ├── routes.py             # APIRouter
       └── validators.py         # Pydantic schemas
   ```

2. Registrar dependencias en `src/__init__.py` (mappers, repositorios, handlers, controladores)

3. Incluir router en `main.py`

4. Crear migracion:
   ```bash
   make migrations m="create nuevo_modulo tables"
   make upgrade
   ```

5. Escribir tests unitarios y de integracion

### Reglas importantes

- Los repositorios se registran con lifetime `SCOPED` para compartir sesion DB por peticion
- Los mappers se registran como `SINGLETON` (son stateless)
- Las entidades de dominio no deben importar codigo de infraestructura
- Los eventos de dominio son el mecanismo para comunicacion entre modulos
- Cada handler crea su propio span de OpenTelemetry automaticamente

### Pull Requests

1. Crear branch desde `master`: `git checkout -b feat/descripcion`
2. Implementar cambios siguiendo la estructura del proyecto
3. Ejecutar tests: `make tests`
4. Ejecutar linter: `make lint`
5. Crear PR con descripcion clara del cambio

## Roadmap

Ver [ROADMAP.md](ROADMAP.md) para el plan completo de evolucion del sistema.

**Modulos implementados**: Catalogo, Inventario, Clientes, Ventas

**Proximos modulos**: Proveedores, Compras, Pricing, Multi-almacen, Reportes

## Licencia

Este proyecto esta licenciado bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para mas detalles.

---

**Desarrollado por Faclab**
