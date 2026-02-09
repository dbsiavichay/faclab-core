# Análisis y Propuesta Arquitectónica - Faclab Core

**Fecha:** 2026-02-06
**Versión:** 1.0
**Autor:** Análisis Arquitectónico con Claude Code

---

## 📋 Tabla de Contenidos

1. [Comprensión del Proyecto](#1-comprensión-del-proyecto)
2. [Evaluación Arquitectónica Actual](#2-evaluación-arquitectónica-actual)
3. [Propuesta de Arquitectura Mejorada](#3-propuesta-de-arquitectura-mejorada)
4. [Plan de Migración](#4-plan-de-migración)
5. [Conclusiones y Recomendaciones](#5-conclusiones-y-recomendaciones)

---

## 1. Comprensión del Proyecto

### 1.1 Contexto del Negocio

**Faclab Core** es un sistema de gestión empresarial que actualmente maneja:
- **Catálogo de productos** (productos y categorías)
- **Inventario** (stock y movimientos)
- **Clientes** (gestión de clientes y contactos)

**Visión futura** (según ROADMAP.md):
- Sistema completo de **ventas** (POS - Punto de Venta)
- Gestión de **compras** y proveedores
- **Precios** dinámicos y promociones
- **Multi-almacén** (múltiples ubicaciones)
- **Reportes** y análisis
- Posiblemente **contabilidad** integrada

### 1.2 Stack Tecnológico Actual

```
Backend:
- Python 3.11+
- FastAPI (framework web)
- SQLAlchemy (ORM)
- PostgreSQL (base de datos)
- Alembic (migraciones)
- Pydantic (validación)

Infraestructura:
- Docker + Docker Compose
- Uvicorn (servidor ASGI)

Arquitectura:
- Clean Architecture (capas)
- Dependency Injection (custom)
- Repository Pattern
- Use Case Pattern
```

### 1.3 Estructura de Directorios Actual

```
faclab-core/
├── config/                      # Configuración por entornos
├── alembic/                     # Migraciones de BD
├── src/
│   ├── shared/                  # Componentes compartidos
│   │   ├── domain/             # Entity base, ports
│   │   ├── app/                # Repository interface
│   │   └── infra/              # DI, BaseRepository, DB, middleware
│   ├── catalog/                # Contexto: Catálogo
│   │   └── product/
│   │       ├── domain/         # Category, Product (entities)
│   │       ├── app/            # Use Cases
│   │       └── infra/          # Controllers, routes, repos, mappers
│   ├── inventory/              # Contexto: Inventario
│   │   ├── stock/
│   │   │   ├── domain/         # Stock (entity)
│   │   │   ├── app/            # Use Cases
│   │   │   └── infra/          # Controllers, routes, repos, mappers
│   │   └── movement/
│   │       ├── domain/         # Movement (entity)
│   │       ├── app/            # Use Cases
│   │       └── infra/          # Controllers, routes, repos, mappers
│   ├── customers/              # Contexto: Clientes
│   │   ├── domain/             # Customer, CustomerContact (entities)
│   │   ├── app/                # Use Cases
│   │   └── infra/              # Controllers, routes, repos, mappers
│   └── __init__.py             # 629 líneas (DI registration)
└── main.py                      # Entry point
```

### 1.4 Flujo de Request Actual

```
HTTP Request → FastAPI Route
    ↓
Route → Controller (via DI dependency)
    ↓
Controller → Use Case (injected)
    ↓
Use Case → Repository (injected)
    ↓
Repository → SQLAlchemy Model → Database
    ↓
Database → Model → Mapper → Entity
    ↓
Entity → Use Case → Controller → Response
```

### 1.5 Patrones Implementados Actualmente

#### Clean Architecture (Capas)
```python
domain/     # Entidades (dataclasses), no dependencias externas
app/        # Casos de uso, interfaces de repositorios
infra/      # Implementaciones concretas (DB, HTTP, etc.)
```

#### Repository Pattern
```python
# Interface
class Repository(Generic[T], ABC):
    @abstractmethod
    def create(self, entity: T) -> T: ...
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]: ...

# Implementación
class BaseRepository(Repository[E], Generic[E]):
    __model__: ClassVar[type[M]]

    def __init__(self, session: Session, mapper: Mapper[E, M]):
        self.session = session
        self.mapper = mapper
```

#### Mapper Pattern
```python
class Mapper(Generic[E, M], ABC):
    @abstractmethod
    def to_entity(self, model: M) -> E: ...
    @abstractmethod
    def to_dict(self, entity: E) -> dict: ...
```

#### Use Case Pattern
```python
class CreateProductUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, product_create: ProductInput) -> ProductOutput:
        product = Product(**product_create)
        product = self.repo.create(product)
        return product.dict()
```

#### Dependency Injection
```python
# Custom DI Container con 3 scopes:
- SINGLETON: compartido (mappers)
- SCOPED: por request (repos, use cases, controllers)
- TRANSIENT: nueva instancia cada vez

# Registro manual en src/__init__.py (629 líneas)
container.register(
    Repository[Product],
    factory=lambda c, scope_id=None: ProductRepositoryImpl(...),
    scope=LifetimeScope.SCOPED
)
```

---

## 2. Evaluación Arquitectónica Actual

Como **experto arquitecto de software**, voy a evaluar la arquitectura actual considerando principios SOLID, DDD, y las necesidades futuras del sistema.

### 2.1 ✅ FORTALEZAS (Lo que está bien)

#### 2.1.1 Separación de Capas Clara ⭐⭐⭐⭐⭐
**Excelente**. La arquitectura sigue Clean Architecture con separación estricta:
- `domain/`: Lógica de negocio pura, sin dependencias externas
- `app/`: Casos de uso, orquestación de lógica
- `infra/`: Detalles de implementación (DB, HTTP, etc.)

**Beneficio**: Fácil de testear, cambiar tecnologías, mantener.

#### 2.1.2 Patrones de Diseño Reconocidos ⭐⭐⭐⭐
**Muy bueno**. Uso correcto de:
- Repository Pattern: abstracción de persistencia
- Mapper Pattern: conversión domain ↔ infra
- Use Case Pattern: lógica de aplicación encapsulada
- Dependency Injection: inversión de control

**Beneficio**: Código mantenible, testeabble, extensible.

#### 2.1.3 Modularización por Contextos de Negocio ⭐⭐⭐⭐
**Muy bueno**. Separación en bounded contexts:
- `catalog/`: productos y categorías
- `inventory/`: stock y movimientos
- `customers/`: clientes y contactos

**Beneficio**: Alineado con Domain-Driven Design (DDD).

#### 2.1.4 Inmutabilidad de Entidades ⭐⭐⭐⭐
**Muy bueno**. Uso de `@dataclass` para entidades:
```python
@dataclass
class Product(Entity):
    name: str
    sku: str
    # ...
```

**Beneficio**: Thread-safety, predecibilidad, facilita testing.

#### 2.1.5 Type Hints y Generics ⭐⭐⭐⭐⭐
**Excelente**. Uso consistente de tipado estático:
```python
Repository[Product]
Generic[T]
Optional[E]
```

**Beneficio**: Autocomplete, detección de errores en desarrollo, mejor mantenibilidad.

### 2.2 ⚠️ DEBILIDADES (Áreas de mejora)

#### 2.2.1 Dependency Injection Verboso ⭐⭐
**Necesita mejora urgente**.

**Problema**: 629 líneas de registro manual en `src/__init__.py`:
```python
# 429 líneas solo para registrar use cases (repetitivo)
container.register(
    CreateProductUseCase,
    factory=lambda c, scope_id=None: CreateProductUseCase(
        c.resolve_scoped(Repository[Product], scope_id)
        if scope_id
        else c.resolve(Repository[Product])
    ),
)
# ... x100 más
```

**Consecuencias**:
- Alto mantenimiento (cada nuevo use case = 8-10 líneas)
- Propenso a errores (copy-paste)
- Difícil de leer y entender
- No escalable (imagine 50 módulos)

**Solución propuesta**: Auto-discovery con decoradores (ver sección 3).

#### 2.2.2 Falta de Domain Events ⭐⭐
**Crítico para crecimiento**.

**Problema**: Acoplamiento directo entre módulos. Ejemplo:
```python
# inventory/movement/app/use_cases.py
class CreateMovementUseCase:
    def execute(self, movement_create):
        movement = self.movement_repo.create(movement)
        # ❌ Directamente modifica stock (acoplamiento)
        stock = self.stock_repo.first(product_id=movement.product_id)
        stock.update_quantity(movement.quantity)
        self.stock_repo.update(stock)
```

**Consecuencias**:
- Sales module tendrá que conocer inventory
- Purchases module tendrá que conocer inventory
- Viola Single Responsibility Principle
- Dificulta testing (mocks complejos)
- No hay audit trail de eventos

**Impacto futuro**: Cuando se implemente `sales`:
```python
# ❌ Mal (acoplamiento directo)
class ConfirmSaleUseCase:
    def __init__(self, sale_repo, movement_repo, stock_repo):
        # Use case conoce 3 módulos diferentes
```

**Solución propuesta**: Event-Driven Architecture con Domain Events (ver sección 3).

#### 2.2.3 Ausencia de Value Objects ⭐⭐⭐
**Importante para lógica de negocio rica**.

**Problema**: Tipos primitivos sin validación:
```python
@dataclass
class Customer(Entity):
    tax_id: str          # ❌ No valida formato
    email: str           # ❌ No valida @
    credit_limit: float  # ❌ Puede ser negativo
```

**Consecuencias**:
- Validación dispersa (controllers, use cases, entities)
- Duplicación de lógica de validación
- Sin garantías de invariantes
- Difícil agregar comportamiento (ej: formatear tax_id)

**Ejemplo del problema**:
```python
# En controller
if not validate_email(customer.email):
    raise ValueError("Invalid email")

# En use case (duplicado)
if not validate_email(customer.email):
    raise ValueError("Invalid email")

# Sin encapsulación de comportamiento
# ¿Cómo calcular si customer tiene crédito disponible?
```

**Solución propuesta**: Value Objects para encapsular validación y comportamiento (ver sección 3).

#### 2.2.4 Sin Patrón Specification ⭐⭐⭐
**Necesario para queries complejas**.

**Problema**: Queries complejas duplicadas o hardcodeadas:
```python
# ❌ Criteria SQL en use cases
movements = movement_repo.filter(
    criteria=[
        MovementModel.product_id == product_id,
        MovementModel.type == "OUT",
        MovementModel.date >= start_date,
        MovementModel.date <= end_date,
    ]
)
```

**Consecuencias**:
- Lógica de queries en capa de aplicación (no dominio)
- Difícil reutilizar queries
- Testing complicado
- No se puede combinar especificaciones

**Ejemplo futuro necesario** (reportes):
```python
# Necesitaremos combinar especificaciones complejas
products_low_stock = ProductInStock() & ProductBelowMinStock() & ProductInCategory(5)
```

**Solución propuesta**: Specification Pattern (ver sección 3).

#### 2.2.5 Falta Unit of Work Explícito ⭐⭐
**Importante para transacciones complejas**.

**Problema**: Manejo de transacciones implícito:
```python
# ❌ Cada operación hace commit
movement = self.movement_repo.create(movement)  # commit
stock = self.stock_repo.update(stock)           # commit

# ¿Qué pasa si stock.update() falla?
# movement ya está committeado (inconsistencia)
```

**Consecuencias**:
- Sin atomicidad garantizada
- Difícil hacer rollback
- Testing complicado (múltiples commits)
- No hay transacciones de larga duración

**Solución propuesta**: Unit of Work Pattern (ver sección 3).

#### 2.2.6 Sin CQRS ⭐⭐
**Necesario para escalar (especialmente reportes)**.

**Problema**: Mismo modelo para comandos y queries:
```python
# ❌ GetAllProductsUseCase retorna entidades completas
products = product_repo.get_all()  # Carga relaciones, lazy loading
```

**Consecuencias**:
- Queries lentas (N+1 problem)
- Reportes complejos difíciles de optimizar
- No se puede cachear fácilmente
- Escalabilidad limitada

**Ejemplo futuro** (reportes de ventas):
```python
# Necesitaremos queries agregadas optimizadas
# No podemos usar Repository[Sale] para esto
sales_report = """
    SELECT
        p.name,
        SUM(si.quantity) as total_sold,
        SUM(si.subtotal) as revenue
    FROM sales s
    JOIN sale_items si ON s.id = si.sale_id
    JOIN products p ON si.product_id = p.id
    WHERE s.sale_date BETWEEN ? AND ?
    GROUP BY p.id
"""
```

**Solución propuesta**: CQRS con Query Objects (ver sección 3).

#### 2.2.7 BaseRepository con Limitaciones ⭐⭐⭐
**Funcional pero mejorable**.

**Problemas menores**:
```python
# 1. Uso de .get() (deprecated en SQLAlchemy 2.0)
model = self.session.query(self.__model__).get(id)  # ❌

# 2. No maneja relaciones lazy loading bien
# 3. filter() retorna List[E] pero podría beneficiarse de paginación real
# 4. Sin soporte para eager loading
# 5. TypeVars M y E confusos (M debería ser type[Base])
```

**Solución propuesta**: Refactorizar BaseRepository (ver sección 3).

### 2.3 🎯 Evaluación General

#### Puntuación por Categoría

| Categoría | Puntuación | Comentario |
|-----------|------------|------------|
| **Separation of Concerns** | 9/10 | Excelente separación de capas |
| **SOLID Principles** | 7/10 | Buen SRP, OCP; mejorar DIP con eventos |
| **DDD Principles** | 6/10 | Buenos bounded contexts; faltan Value Objects, Domain Events |
| **Testability** | 7/10 | Buena con dependency injection; mejorable con UoW |
| **Maintainability** | 6/10 | DI verboso, sin auto-discovery |
| **Scalability** | 5/10 | Sin CQRS, sin eventos, sin cache strategy |
| **Extensibility** | 7/10 | Fácil agregar módulos; difícil agregar features cross-cutting |
| **Code Quality** | 8/10 | Type hints excelentes, código limpio |

**Promedio: 6.9/10** - **Bueno, pero necesita mejoras para escalar**

#### Veredicto Final

> **La arquitectura actual es SÓLIDA para un proyecto pequeño/mediano** (hasta 5-10 módulos, 2-3 desarrolladores).
>
> **SIN EMBARGO**, para un sistema empresarial completo de ventas, inventario, POS y contabilidad con:
> - 15+ módulos (ventas, compras, pricing, warehouse, reportes, contabilidad, etc.)
> - Múltiples equipos de desarrollo
> - Alto volumen de transacciones
> - Necesidad de auditoría (contabilidad)
> - Reportes complejos en tiempo real
>
> **La arquitectura necesita EVOLUCIONAR** con:
> 1. **Domain Events** (desacoplamiento)
> 2. **CQRS** (escalabilidad de queries)
> 3. **Value Objects** (lógica de negocio rica)
> 4. **Unit of Work** (transacciones complejas)
> 5. **Simplificación del DI** (auto-discovery)
> 6. **Specification Pattern** (queries reutilizables)

---

## 3. Propuesta de Arquitectura Mejorada

### 3.1 Visión General de la Nueva Arquitectura

#### Arquitectura Hexagonal (Ports & Adapters) Mejorada

```
┌─────────────────────────────────────────────────────────────┐
│                        Application Layer                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Driving Adapters (HTTP)                 │   │
│  │  FastAPI Controllers → Commands/Queries → Handlers  │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                        Domain Layer                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Entities │ Value Objects │ Domain Services         │   │
│  │  Domain Events │ Specifications │ Aggregates        │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Application Services                      │
│  ┌─────────────────────┬──────────────────────────────┐   │
│  │  Command Handlers   │  Query Handlers              │   │
│  │  (Write Operations) │  (Read Operations - CQRS)    │   │
│  └─────────────────────┴──────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Event Handlers │ Subscribers │ Sagas               │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│  ┌─────────────────────┬──────────────────────────────┐   │
│  │  Repositories       │  Query Services              │   │
│  │  (Write Model)      │  (Read Model)                │   │
│  └─────────────────────┴──────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Event Store │ Message Bus │ Unit of Work          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Patrón 1: Domain Events (Desacoplamiento)

#### Problema que resuelve
- Elimina acoplamiento directo entre módulos
- Permite reaccionar a cambios sin conocer implementación
- Facilita auditoría y debugging
- Soporta procesamiento asíncrono

#### Implementación

##### 3.2.1 Base de Domain Events
```python
# src/shared/domain/events.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)
    aggregate_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': str(self.event_id),
            'event_type': self.__class__.__name__,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': self.aggregate_id,
            'payload': self._payload()
        }

    def _payload(self) -> Dict[str, Any]:
        """Override in subclasses to provide event-specific data."""
        return {}
```

##### 3.2.2 Eventos de Negocio Específicos
```python
# src/sales/domain/events.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SaleConfirmed(DomainEvent):
    """Event emitted when a sale is confirmed."""
    sale_id: int
    customer_id: int
    warehouse_id: int
    items: List[Dict[str, Any]]  # [{product_id, quantity, unit_price}]
    total: float

    def _payload(self) -> Dict[str, Any]:
        return {
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'warehouse_id': self.warehouse_id,
            'items': self.items,
            'total': self.total
        }

@dataclass
class SaleCancelled(DomainEvent):
    """Event emitted when a sale is cancelled."""
    sale_id: int
    reason: str
    items: List[Dict[str, Any]]

@dataclass
class PaymentReceived(DomainEvent):
    """Event emitted when a payment is registered."""
    payment_id: int
    sale_id: int
    amount: float
    payment_method: str
```

##### 3.2.3 Event Bus (In-Memory + Optional Async)
```python
# src/shared/infra/events/event_bus.py
from typing import Callable, Dict, List, Type
from src.shared.domain.events import DomainEvent
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """In-process event bus for domain events."""

    _handlers: Dict[Type[DomainEvent], List[Callable]] = {}
    _async_handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def subscribe(
        cls,
        event_type: Type[DomainEvent],
        handler: Callable[[DomainEvent], None],
        async_mode: bool = False
    ) -> None:
        """Subscribe a handler to an event type."""
        handlers_dict = cls._async_handlers if async_mode else cls._handlers

        if event_type not in handlers_dict:
            handlers_dict[event_type] = []

        handlers_dict[event_type].append(handler)
        logger.info(
            f"Subscribed {handler.__name__} to {event_type.__name__} "
            f"({'async' if async_mode else 'sync'})"
        )

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        """Publish an event to all subscribers (synchronous)."""
        event_type = type(event)
        logger.info(f"Publishing event: {event_type.__name__} (ID: {event.event_id})")

        # Execute synchronous handlers
        if event_type in cls._handlers:
            for handler in cls._handlers[event_type]:
                try:
                    logger.debug(f"Executing handler: {handler.__name__}")
                    handler(event)
                except Exception as e:
                    logger.error(
                        f"Error in handler {handler.__name__} "
                        f"for event {event_type.__name__}: {str(e)}"
                    )
                    # Continue with other handlers

        # Queue async handlers (future: use Celery/RQ)
        if event_type in cls._async_handlers:
            for handler in cls._async_handlers[event_type]:
                # For now, execute synchronously
                # TODO: Replace with task queue
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in async handler: {str(e)}")

    @classmethod
    def clear(cls) -> None:
        """Clear all subscribers (useful for testing)."""
        cls._handlers.clear()
        cls._async_handlers.clear()
```

##### 3.2.4 Decorador para Event Handlers
```python
# src/shared/infra/events/decorators.py
from typing import Type, Callable
from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus

def event_handler(
    event_type: Type[DomainEvent],
    async_mode: bool = False
) -> Callable:
    """Decorator to register an event handler."""
    def decorator(func: Callable) -> Callable:
        EventBus.subscribe(event_type, func, async_mode)
        return func
    return decorator
```

##### 3.2.5 Uso en Use Cases
```python
# src/sales/app/commands/confirm_sale.py
from src.shared.infra.events.event_bus import EventBus
from src.sales.domain.events import SaleConfirmed

class ConfirmSaleCommandHandler:
    def __init__(self, sale_repo: Repository[Sale]):
        self.sale_repo = sale_repo

    def handle(self, command: ConfirmSaleCommand) -> SaleResponse:
        # 1. Get sale
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundException("Sale not found")

        # 2. Validate
        if sale.status != SaleStatus.DRAFT:
            raise BusinessRuleViolation("Only draft sales can be confirmed")

        # 3. Confirm sale
        sale.status = SaleStatus.CONFIRMED
        sale = self.sale_repo.update(sale)

        # 4. Emit event (NO acoplamiento con inventory)
        event = SaleConfirmed(
            aggregate_id=sale.id,
            sale_id=sale.id,
            customer_id=sale.customer_id,
            warehouse_id=sale.warehouse_id,
            items=[{
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price
            } for item in sale.items],
            total=sale.total
        )
        EventBus.publish(event)

        return SaleResponse.from_entity(sale)
```

##### 3.2.6 Event Handlers en Inventory
```python
# src/inventory/infra/event_handlers.py
from src.sales.domain.events import SaleConfirmed, SaleCancelled
from src.shared.infra.events.decorators import event_handler
from src.inventory.app.commands.create_movement import CreateMovementCommandHandler
from src.inventory.domain.constants import MovementType
from src import container

@event_handler(SaleConfirmed)
def handle_sale_confirmed(event: SaleConfirmed) -> None:
    """When a sale is confirmed, create inventory movements (OUT)."""
    movement_handler = container.resolve(CreateMovementCommandHandler)

    for item in event.items:
        movement_handler.handle(
            CreateMovementCommand(
                product_id=item['product_id'],
                warehouse_id=event.warehouse_id,
                type=MovementType.OUT,
                quantity=item['quantity'],
                reference_type='SALE',
                reference_id=event.sale_id
            )
        )

@event_handler(SaleCancelled)
def handle_sale_cancelled(event: SaleCancelled) -> None:
    """When a sale is cancelled, reverse inventory movements (IN)."""
    movement_handler = container.resolve(CreateMovementCommandHandler)

    for item in event.items:
        movement_handler.handle(
            CreateMovementCommand(
                product_id=item['product_id'],
                warehouse_id=event.warehouse_id,
                type=MovementType.IN,
                quantity=item['quantity'],
                reference_type='SALE_CANCELLATION',
                reference_id=event.sale_id
            )
        )
```

**Beneficios**:
- Sales module NO conoce inventory module
- Fácil agregar nuevos subscribers (ej: notificaciones, auditoría)
- Testeable (mock EventBus)
- Escalable (puede volverse async con Celery/RabbitMQ)

### 3.3 Patrón 2: Value Objects

#### Problema que resuelve
- Encapsula validación de tipos primitivos
- Garantiza invariantes de negocio
- Agrega comportamiento relacionado
- Facilita testing y reutilización

#### Implementación

##### 3.3.1 Base Value Object
```python
# src/shared/domain/value_objects.py
from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for all value objects (immutable)."""

    def __post_init__(self):
        """Validate after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Override in subclasses to add validation."""
        pass
```

##### 3.3.2 Value Objects Comunes
```python
# src/shared/domain/value_objects.py
from decimal import Decimal
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Money(ValueObject):
    """Represents a monetary amount with currency."""
    amount: Decimal
    currency: str = "USD"

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code (ISO 4217)")

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __truediv__(self, divisor: float) -> 'Money':
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

@dataclass(frozen=True)
class Email(ValueObject):
    """Represents an email address."""
    value: str

    def _validate(self) -> None:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def domain(self) -> str:
        """Extract domain from email."""
        return self.value.split('@')[1]

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class TaxId(ValueObject):
    """Represents a tax identification number."""
    value: str
    country: str = "EC"  # Ecuador by default

    def _validate(self) -> None:
        if self.country == "EC":
            # Ecuadorian RUC: 13 digits
            if not re.match(r'^\d{13}$', self.value):
                raise ValueError(
                    f"Invalid Ecuadorian RUC: {self.value}. Must be 13 digits."
                )
        # Add validations for other countries

    def formatted(self) -> str:
        """Format tax ID for display."""
        if self.country == "EC":
            # Format as XXX-XXXXXXX-XXX
            return f"{self.value[:3]}-{self.value[3:10]}-{self.value[10:]}"
        return self.value

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """Represents a phone number."""
    value: str
    country_code: str = "+593"  # Ecuador

    def _validate(self) -> None:
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', self.value)
        if not re.match(r'^\+?\d{7,15}$', cleaned):
            raise ValueError(f"Invalid phone number: {self.value}")
        object.__setattr__(self, 'value', cleaned)

    def international(self) -> str:
        """Return in international format."""
        if not self.value.startswith('+'):
            return f"{self.country_code}{self.value}"
        return self.value

    def __str__(self) -> str:
        return self.international()

@dataclass(frozen=True)
class Percentage(ValueObject):
    """Represents a percentage (0-100)."""
    value: Decimal

    def _validate(self) -> None:
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        if not 0 <= self.value <= 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {self.value}")

    def as_decimal(self) -> Decimal:
        """Convert to decimal (e.g., 15% -> 0.15)."""
        return self.value / Decimal('100')

    def apply_to(self, amount: Money) -> Money:
        """Apply percentage to a monetary amount."""
        return amount * float(self.as_decimal())

    def __str__(self) -> str:
        return f"{self.value}%"
```

##### 3.3.3 Uso en Entidades
```python
# src/customers/domain/entities.py
from dataclasses import dataclass
from typing import Optional
from src.shared.domain.entities import Entity
from src.shared.domain.value_objects import Email, TaxId, PhoneNumber, Money

@dataclass
class Customer(Entity):
    name: str
    tax_id: TaxId
    email: Email
    phone: PhoneNumber
    credit_limit: Money
    payment_terms: int  # days
    is_active: bool = True
    id: Optional[int] = None

    def has_available_credit(self, amount: Money) -> bool:
        """Check if customer has enough credit."""
        # This business logic is now in the entity
        return self.credit_limit.amount >= amount.amount

    def formatted_contact_info(self) -> str:
        """Return formatted contact information."""
        return f"""
        Name: {self.name}
        Tax ID: {self.tax_id.formatted()}
        Email: {self.email}
        Phone: {self.phone.international()}
        Credit Limit: {self.credit_limit}
        """
```

**Beneficios**:
- Validación centralizada (no duplicada)
- Comportamiento encapsulado (Money.add, TaxId.formatted)
- Inmutable (thread-safe)
- Fácil de testear
- Expresivo (Money vs float, Email vs str)

### 3.4 Patrón 3: CQRS (Command Query Responsibility Segregation)

#### Problema que resuelve
- Queries complejas optimizadas (reportes)
- Escalabilidad (read replicas, cache)
- Separación de responsabilidades
- No contamina modelo de dominio con DTOs

#### Implementación

##### 3.4.1 Commands (Write Side)
```python
# src/shared/app/commands.py
from dataclasses import dataclass
from abc import ABC

@dataclass
class Command(ABC):
    """Base class for all commands (write operations)."""
    pass

# src/sales/app/commands/create_sale.py
@dataclass
class CreateSaleCommand(Command):
    customer_id: int
    warehouse_id: int

@dataclass
class AddSaleItemCommand(Command):
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float

@dataclass
class ConfirmSaleCommand(Command):
    sale_id: int
```

##### 3.4.2 Command Handlers
```python
# src/shared/app/handlers.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TCommand = TypeVar('TCommand', bound='Command')
TResult = TypeVar('TResult')

class CommandHandler(Generic[TCommand, TResult], ABC):
    """Base class for command handlers."""

    @abstractmethod
    def handle(self, command: TCommand) -> TResult:
        """Handle a command and return result."""
        pass

# src/sales/app/commands/create_sale.py
class CreateSaleCommandHandler(CommandHandler[CreateSaleCommand, SaleResponse]):
    def __init__(
        self,
        sale_repo: Repository[Sale],
        customer_repo: Repository[Customer]
    ):
        self.sale_repo = sale_repo
        self.customer_repo = customer_repo

    def handle(self, command: CreateSaleCommand) -> SaleResponse:
        # Validate customer exists
        customer = self.customer_repo.get_by_id(command.customer_id)
        if not customer:
            raise NotFoundException("Customer not found")

        # Create sale
        sale = Sale(
            customer_id=command.customer_id,
            warehouse_id=command.warehouse_id,
            status=SaleStatus.DRAFT,
            sale_date=datetime.now()
        )
        sale = self.sale_repo.create(sale)

        return SaleResponse.from_entity(sale)
```

##### 3.4.3 Queries (Read Side)
```python
# src/shared/app/queries.py
from dataclasses import dataclass
from abc import ABC

@dataclass
class Query(ABC):
    """Base class for all queries (read operations)."""
    pass

# src/sales/app/queries/get_sales_report.py
from datetime import date

@dataclass
class GetSalesReportQuery(Query):
    start_date: date
    end_date: date
    customer_id: Optional[int] = None
    product_id: Optional[int] = None

@dataclass
class GetTopProductsQuery(Query):
    start_date: date
    end_date: date
    limit: int = 10

@dataclass
class GetCustomerSalesHistoryQuery(Query):
    customer_id: int
    limit: Optional[int] = None
    offset: Optional[int] = None
```

##### 3.4.4 Query Handlers con SQL Directo
```python
# src/shared/infra/queries.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from sqlalchemy.orm import Session

TQuery = TypeVar('TQuery', bound='Query')
TResult = TypeVar('TResult')

class QueryHandler(Generic[TQuery, TResult], ABC):
    """Base class for query handlers."""

    @abstractmethod
    def handle(self, query: TQuery) -> TResult:
        """Handle a query and return result."""
        pass

# src/sales/infra/queries/sales_report_query_handler.py
from sqlalchemy import text

@dataclass
class SalesReportRow:
    product_id: int
    product_name: str
    total_quantity: int
    total_revenue: Decimal
    avg_unit_price: Decimal

class GetSalesReportQueryHandler(QueryHandler[GetSalesReportQuery, List[SalesReportRow]]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetSalesReportQuery) -> List[SalesReportRow]:
        # Optimized SQL query (no ORM overhead)
        sql = text("""
            SELECT
                p.id as product_id,
                p.name as product_name,
                SUM(si.quantity) as total_quantity,
                SUM(si.subtotal) as total_revenue,
                AVG(si.unit_price) as avg_unit_price
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE s.sale_date BETWEEN :start_date AND :end_date
                AND s.status = 'CONFIRMED'
                AND (:customer_id IS NULL OR s.customer_id = :customer_id)
                AND (:product_id IS NULL OR p.id = :product_id)
            GROUP BY p.id, p.name
            ORDER BY total_revenue DESC
        """)

        result = self.session.execute(
            sql,
            {
                'start_date': query.start_date,
                'end_date': query.end_date,
                'customer_id': query.customer_id,
                'product_id': query.product_id
            }
        )

        return [
            SalesReportRow(
                product_id=row.product_id,
                product_name=row.product_name,
                total_quantity=row.total_quantity,
                total_revenue=row.total_revenue,
                avg_unit_price=row.avg_unit_price
            )
            for row in result
        ]
```

##### 3.4.5 Command/Query Bus (opcional)
```python
# src/shared/infra/buses/command_bus.py
from typing import Dict, Type
from src.shared.app.commands import Command
from src.shared.app.handlers import CommandHandler

class CommandBus:
    """Central command bus for dispatching commands to handlers."""

    _handlers: Dict[Type[Command], CommandHandler] = {}

    @classmethod
    def register(cls, command_type: Type[Command], handler: CommandHandler) -> None:
        """Register a command handler."""
        cls._handlers[command_type] = handler

    @classmethod
    def dispatch(cls, command: Command):
        """Dispatch a command to its handler."""
        command_type = type(command)
        if command_type not in cls._handlers:
            raise ValueError(f"No handler registered for {command_type.__name__}")

        handler = cls._handlers[command_type]
        return handler.handle(command)

# Similar for QueryBus
```

**Beneficios**:
- Queries optimizadas sin ORM overhead
- Fácil cachear queries
- Read replicas para queries
- Comandos y queries separados (clarity)
- Escalabilidad horizontal

### 3.5 Patrón 4: Unit of Work

#### Problema que resuelve
- Transacciones atómicas con múltiples repositories
- Rollback automático en errores
- Testing más fácil (mock UoW)
- Control explícito de commit

#### Implementación

##### 3.5.1 Interface Unit of Work
```python
# src/shared/app/unit_of_work.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class UnitOfWork(ABC):
    """Abstract base class for Unit of Work pattern."""

    @abstractmethod
    def __enter__(self):
        """Enter context manager."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        pass
```

##### 3.5.2 SQLAlchemy Unit of Work
```python
# src/shared/infra/unit_of_work.py
from sqlalchemy.orm import Session
from src.shared.app.unit_of_work import UnitOfWork

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self) -> None:
        """Commit the transaction."""
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""
        if self.session:
            self.session.rollback()

    # Lazy-loaded repositories
    @property
    def sales(self) -> Repository[Sale]:
        return SaleRepositoryImpl(self.session, SaleMapper())

    @property
    def customers(self) -> Repository[Customer]:
        return CustomerRepositoryImpl(self.session, CustomerMapper())

    @property
    def movements(self) -> Repository[Movement]:
        return MovementRepositoryImpl(self.session, MovementMapper())

    @property
    def stocks(self) -> Repository[Stock]:
        return StockRepositoryImpl(self.session, StockMapper())
```

##### 3.5.3 Uso en Command Handlers
```python
# src/sales/app/commands/confirm_sale.py
class ConfirmSaleCommandHandler(CommandHandler[ConfirmSaleCommand, SaleResponse]):
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self.uow_factory = uow_factory

    def handle(self, command: ConfirmSaleCommand) -> SaleResponse:
        with self.uow_factory() as uow:
            # 1. Get sale
            sale = uow.sales.get_by_id(command.sale_id)
            if not sale:
                raise NotFoundException("Sale not found")

            # 2. Validate stock for all items
            for item in sale.items:
                stock = uow.stocks.first(
                    product_id=item.product_id,
                    warehouse_id=sale.warehouse_id
                )
                if not stock or stock.quantity < item.quantity:
                    raise InsufficientStockError(
                        f"Insufficient stock for product {item.product_id}"
                    )

            # 3. Confirm sale
            sale.status = SaleStatus.CONFIRMED
            sale = uow.sales.update(sale)

            # 4. Create movements (within same transaction)
            for item in sale.items:
                movement = Movement(
                    product_id=item.product_id,
                    warehouse_id=sale.warehouse_id,
                    type=MovementType.OUT,
                    quantity=item.quantity,
                    reference_type='SALE',
                    reference_id=sale.id,
                    date=datetime.now()
                )
                uow.movements.create(movement)

                # 5. Update stock
                stock = uow.stocks.first(
                    product_id=item.product_id,
                    warehouse_id=sale.warehouse_id
                )
                stock.quantity -= item.quantity
                uow.stocks.update(stock)

            # 6. Commit everything (or rollback if any error)
            uow.commit()

            # 7. Emit event (after commit)
            EventBus.publish(SaleConfirmed(
                aggregate_id=sale.id,
                sale_id=sale.id,
                customer_id=sale.customer_id,
                warehouse_id=sale.warehouse_id,
                items=[{
                    'product_id': item.product_id,
                    'quantity': item.quantity
                } for item in sale.items],
                total=sale.total
            ))

            return SaleResponse.from_entity(sale)
```

**Beneficios**:
- Transacciones atómicas garantizadas
- Rollback automático en excepciones
- Testing más fácil (mock UoW)
- Explícito (no commits ocultos)

### 3.6 Patrón 5: Specification Pattern

#### Problema que resuelve
- Queries complejas reutilizables
- Lógica de filtrado en dominio (no infra)
- Composición de criterios (AND, OR, NOT)
- Testing más fácil

#### Implementación

##### 3.6.1 Base Specification
```python
# src/shared/domain/specifications.py
from abc import ABC, abstractmethod
from typing import List, Any, Union

class Specification(ABC):
    """Base class for specifications (business rules as objects)."""

    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if candidate satisfies the specification (in-memory)."""
        pass

    @abstractmethod
    def to_sql_criteria(self) -> List[Any]:
        """Convert specification to SQLAlchemy criteria."""
        pass

    def and_(self, other: 'Specification') -> 'AndSpecification':
        """Combine with AND."""
        return AndSpecification(self, other)

    def or_(self, other: 'Specification') -> 'OrSpecification':
        """Combine with OR."""
        return OrSpecification(self, other)

    def not_(self) -> 'NotSpecification':
        """Negate specification."""
        return NotSpecification(self)

    # Operator overloading
    def __and__(self, other: 'Specification') -> 'AndSpecification':
        return self.and_(other)

    def __or__(self, other: 'Specification') -> 'OrSpecification':
        return self.or_(other)

    def __invert__(self) -> 'NotSpecification':
        return self.not_()

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return (
            self.left.is_satisfied_by(candidate) and
            self.right.is_satisfied_by(candidate)
        )

    def to_sql_criteria(self) -> List[Any]:
        return [*self.left.to_sql_criteria(), *self.right.to_sql_criteria()]

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return (
            self.left.is_satisfied_by(candidate) or
            self.right.is_satisfied_by(candidate)
        )

    def to_sql_criteria(self) -> List[Any]:
        from sqlalchemy import or_
        return [or_(*self.left.to_sql_criteria(), *self.right.to_sql_criteria())]

class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def to_sql_criteria(self) -> List[Any]:
        from sqlalchemy import not_
        return [not_(*self.spec.to_sql_criteria())]
```

##### 3.6.2 Specifications de Negocio
```python
# src/catalog/domain/specifications.py
from src.shared.domain.specifications import Specification
from src.catalog.product.infra.models import ProductModel, CategoryModel
from src.inventory.stock.infra.models import StockModel

class ProductInStock(Specification):
    """Products with available stock."""

    def is_satisfied_by(self, product) -> bool:
        return product.stock and product.stock.quantity > 0

    def to_sql_criteria(self) -> List[Any]:
        return [StockModel.quantity > 0]

class ProductInCategory(Specification):
    """Products in a specific category."""

    def __init__(self, category_id: int):
        self.category_id = category_id

    def is_satisfied_by(self, product) -> bool:
        return product.category_id == self.category_id

    def to_sql_criteria(self) -> List[Any]:
        return [ProductModel.category_id == self.category_id]

class ProductPriceBetween(Specification):
    """Products with price in a range."""

    def __init__(self, min_price: Decimal, max_price: Decimal):
        self.min_price = min_price
        self.max_price = max_price

    def is_satisfied_by(self, product) -> bool:
        return self.min_price <= product.price.amount <= self.max_price

    def to_sql_criteria(self) -> List[Any]:
        from src.pricing.infra.models import ProductPriceModel
        return [
            ProductPriceModel.base_price >= self.min_price,
            ProductPriceModel.base_price <= self.max_price
        ]

class ProductActiveAndAvailable(Specification):
    """Products that are active and have stock."""

    def is_satisfied_by(self, product) -> bool:
        return product.is_active and product.stock.quantity > 0

    def to_sql_criteria(self) -> List[Any]:
        return [
            ProductModel.is_active == True,
            StockModel.quantity > 0
        ]
```

##### 3.6.3 Repository con Specifications
```python
# src/shared/infra/repositories.py (mejorado)
class BaseRepository(Repository[E], Generic[E]):
    # ... existing methods ...

    def filter_by_spec(
        self,
        spec: Specification,
        order_by: Optional[str] = None,
        desc_order: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[E]:
        """Filter entities using a specification."""
        criteria = spec.to_sql_criteria()
        return self.filter(criteria, order_by, desc_order, limit, offset)

    def first_by_spec(self, spec: Specification) -> Optional[E]:
        """Get first entity matching specification."""
        results = self.filter_by_spec(spec, limit=1)
        return results[0] if results else None

    def count_by_spec(self, spec: Specification) -> int:
        """Count entities matching specification."""
        criteria = spec.to_sql_criteria()
        return self.session.query(self.__model__).filter(*criteria).count()
```

##### 3.6.4 Uso en Use Cases
```python
# src/catalog/app/queries/search_products.py
class SearchProductsQueryHandler:
    def __init__(self, product_repo: Repository[Product]):
        self.product_repo = product_repo

    def handle(self, query: SearchProductsQuery) -> List[ProductResponse]:
        # Build specification dynamically
        spec = ProductActiveAndAvailable()

        if query.category_id:
            spec = spec & ProductInCategory(query.category_id)

        if query.min_price and query.max_price:
            spec = spec & ProductPriceBetween(query.min_price, query.max_price)

        # Execute
        products = self.product_repo.filter_by_spec(
            spec,
            order_by='name',
            limit=query.limit,
            offset=query.offset
        )

        return [ProductResponse.from_entity(p) for p in products]
```

**Beneficios**:
- Lógica de negocio en dominio (no en queries SQL)
- Reutilizable y composable
- Testeable (in-memory checks)
- Expresivo (ProductInStock() & ProductInCategory(5))

### 3.7 Patrón 6: Simplificación del DI con Decoradores

#### Problema que resuelve
- DI verboso (629 líneas)
- Auto-discovery de componentes
- Menos boilerplate

#### Implementación

##### 3.7.1 Decoradores DI
```python
# src/shared/infra/di/decorators.py
from src.shared.infra.di import DependencyContainer, LifetimeScope
from typing import Type, Callable

# Global container
_container = DependencyContainer()

def singleton(cls: Type) -> Type:
    """Register a class as singleton."""
    _container.register(
        cls,
        factory=lambda c: cls(),
        scope=LifetimeScope.SINGLETON
    )
    return cls

def scoped(cls: Type) -> Type:
    """Register a class as scoped (per-request)."""
    # Auto-resolve dependencies from __init__
    _container.register(
        cls,
        factory=lambda c, scope_id=None: _auto_resolve(c, cls, scope_id),
        scope=LifetimeScope.SCOPED
    )
    return cls

def transient(cls: Type) -> Type:
    """Register a class as transient."""
    _container.register(
        cls,
        factory=lambda c: _auto_resolve(c, cls, None),
        scope=LifetimeScope.TRANSIENT
    )
    return cls

def _auto_resolve(container: DependencyContainer, cls: Type, scope_id):
    """Auto-resolve constructor dependencies."""
    import inspect
    sig = inspect.signature(cls.__init__)
    params = {}

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        param_type = param.annotation
        if param_type != inspect.Parameter.empty:
            if scope_id:
                params[param_name] = container.resolve_scoped(param_type, scope_id)
            else:
                params[param_name] = container.resolve(param_type)

    return cls(**params)

def repository(entity_type: Type):
    """Register a repository implementation."""
    def decorator(cls: Type) -> Type:
        _container.register(
            Repository[entity_type],
            factory=lambda c, scope_id=None: _auto_resolve(c, cls, scope_id),
            scope=LifetimeScope.SCOPED
        )
        return cls
    return decorator
```

##### 3.7.2 Uso con Decoradores
```python
# src/catalog/product/infra/mappers.py
@singleton
class ProductMapper(Mapper[Product, ProductModel]):
    def to_entity(self, model: ProductModel) -> Product:
        # ...

# src/catalog/product/infra/repositories.py
@repository(Product)
class ProductRepositoryImpl(BaseRepository[Product]):
    __model__ = ProductModel

    # Constructor con auto-resolution
    def __init__(self, session: Session, mapper: ProductMapper):
        super().__init__(session, mapper)

# src/catalog/product/app/commands/create_product.py
@scoped
class CreateProductCommandHandler(CommandHandler[CreateProductCommand, ProductResponse]):
    # Auto-resolved
    def __init__(self, product_repo: Repository[Product]):
        self.product_repo = product_repo

    def handle(self, command: CreateProductCommand) -> ProductResponse:
        # ...
```

##### 3.7.3 Resultado
```python
# src/__init__.py (antes: 629 líneas, después: ~50 líneas)

from src.shared.infra.di.decorators import _container as container
from src.shared.infra.db import Base, get_db_session
from config import config

def initialize():
    """Initialize application (auto-discovery already happened)."""
    db_connection_string = config.DB_CONNECTION_STRING
    if not db_connection_string:
        raise ValueError("Database connection string not found")

    container.configure_db(db_connection_string)

    # Register event handlers
    import src.inventory.infra.event_handlers
    import src.sales.infra.event_handlers
    # ... (auto-discovery can be improved further)

# ✅ Ya no necesitamos init_mappers, init_repositories, init_use_cases, init_controllers
```

**Beneficios**:
- 90% menos código de registro
- Auto-discovery de dependencias
- Más declarativo (@scoped vs manual registration)
- Menos errores (no copy-paste)

### 3.8 Nueva Estructura de Directorios

```
faclab-core/
├── config/
├── alembic/
├── src/
│   ├── shared/                          # Shared Kernel
│   │   ├── domain/
│   │   │   ├── entities.py             # Base Entity
│   │   │   ├── value_objects.py        # Money, Email, TaxId, etc.
│   │   │   ├── events.py               # Base DomainEvent
│   │   │   ├── specifications.py       # Base Specification
│   │   │   ├── exceptions.py           # Domain exceptions
│   │   │   └── ports.py                # Logger port
│   │   ├── app/
│   │   │   ├── repositories.py         # Repository interface
│   │   │   ├── commands.py             # Base Command
│   │   │   ├── queries.py              # Base Query
│   │   │   ├── handlers.py             # CommandHandler, QueryHandler
│   │   │   └── unit_of_work.py         # UnitOfWork interface
│   │   └── infra/
│   │       ├── di/
│   │       │   ├── container.py        # DependencyContainer
│   │       │   └── decorators.py       # @singleton, @scoped, etc.
│   │       ├── events/
│   │       │   ├── event_bus.py        # EventBus
│   │       │   └── decorators.py       # @event_handler
│   │       ├── buses/
│   │       │   ├── command_bus.py      # CommandBus (optional)
│   │       │   └── query_bus.py        # QueryBus (optional)
│   │       ├── db.py                   # Database session, Base
│   │       ├── repositories.py         # BaseRepository
│   │       ├── unit_of_work.py         # SQLAlchemyUnitOfWork
│   │       ├── mappers.py              # Mapper interface
│   │       ├── middlewares.py          # FastAPI middlewares
│   │       ├── exceptions.py           # HTTP exceptions
│   │       └── validators.py           # Base validators
│   │
│   ├── catalog/                         # Bounded Context: Catalog
│   │   └── product/
│   │       ├── domain/
│   │       │   ├── entities.py         # Product, Category
│   │       │   ├── specifications.py   # ProductInStock, etc.
│   │       │   └── events.py           # ProductCreated, etc.
│   │       ├── app/
│   │       │   ├── commands/           # CreateProduct, UpdateProduct
│   │       │   └── queries/            # GetProducts, SearchProducts
│   │       └── infra/
│   │           ├── models.py           # SQLAlchemy models
│   │           ├── mappers.py          # ProductMapper, CategoryMapper
│   │           ├── repositories.py     # ProductRepositoryImpl
│   │           ├── controllers.py      # HTTP controllers
│   │           ├── routes.py           # FastAPI routes
│   │           └── validators.py       # Pydantic models
│   │
│   ├── inventory/                       # Bounded Context: Inventory
│   │   ├── stock/
│   │   │   ├── domain/
│   │   │   │   ├── entities.py         # Stock
│   │   │   │   ├── specifications.py   # LowStock, etc.
│   │   │   │   └── events.py           # StockUpdated, etc.
│   │   │   ├── app/
│   │   │   │   ├── commands/           # UpdateStock
│   │   │   │   └── queries/            # GetStockByProduct
│   │   │   └── infra/
│   │   │       ├── models.py
│   │   │       ├── mappers.py
│   │   │       ├── repositories.py
│   │   │       ├── controllers.py
│   │   │       ├── routes.py
│   │   │       ├── validators.py
│   │   │       └── event_handlers.py   # Handle inventory events
│   │   └── movement/
│   │       ├── domain/
│   │       │   ├── entities.py         # Movement
│   │       │   ├── constants.py        # MovementType enum
│   │       │   ├── events.py           # MovementCreated
│   │       │   └── exceptions.py       # InsufficientStock
│   │       ├── app/
│   │       │   ├── commands/           # CreateMovement
│   │       │   └── queries/            # GetMovements
│   │       └── infra/
│   │           ├── models.py
│   │           ├── mappers.py
│   │           ├── repositories.py
│   │           ├── controllers.py
│   │           ├── routes.py
│   │           └── validators.py
│   │
│   ├── customers/                       # Bounded Context: Customers
│   │   ├── domain/
│   │   │   ├── entities.py             # Customer, CustomerContact
│   │   │   ├── specifications.py       # ActiveCustomers, etc.
│   │   │   └── events.py               # CustomerCreated, etc.
│   │   ├── app/
│   │   │   ├── commands/               # CreateCustomer, UpdateCustomer
│   │   │   └── queries/                # GetCustomers, SearchCustomers
│   │   └── infra/
│   │       ├── models.py
│   │       ├── mappers.py
│   │       ├── repositories.py
│   │       ├── controllers.py
│   │       ├── routes.py
│   │       └── validators.py
│   │
│   ├── sales/                           # Bounded Context: Sales (NUEVO)
│   │   ├── domain/
│   │   │   ├── entities.py             # Sale, SaleItem, Payment
│   │   │   ├── value_objects.py        # SaleTotal, SaleStatus
│   │   │   ├── events.py               # SaleConfirmed, SaleCancelled
│   │   │   ├── specifications.py       # PendingSales, etc.
│   │   │   └── exceptions.py           # SaleAlreadyConfirmed, etc.
│   │   ├── app/
│   │   │   ├── commands/
│   │   │   │   ├── create_sale.py
│   │   │   │   ├── add_sale_item.py
│   │   │   │   ├── confirm_sale.py
│   │   │   │   ├── cancel_sale.py
│   │   │   │   └── register_payment.py
│   │   │   └── queries/
│   │   │       ├── get_sales.py
│   │   │       ├── get_sale_by_id.py
│   │   │       └── get_customer_sales.py
│   │   └── infra/
│   │       ├── models.py
│   │       ├── mappers.py
│   │       ├── repositories.py
│   │       ├── controllers.py
│   │       ├── routes.py
│   │       ├── validators.py
│   │       └── event_handlers.py       # Handle sales events
│   │
│   ├── purchases/                       # Bounded Context: Purchases (FUTURO)
│   ├── suppliers/                       # Bounded Context: Suppliers (FUTURO)
│   ├── pricing/                         # Bounded Context: Pricing (FUTURO)
│   ├── warehouse/                       # Bounded Context: Warehouse (FUTURO)
│   ├── reporting/                       # Bounded Context: Reporting (FUTURO)
│   │   └── infra/
│   │       └── queries/                # Optimized SQL queries
│   └── accounting/                      # Bounded Context: Accounting (FUTURO)
│
└── main.py
```

### 3.9 Resumen de Patrones Propuestos

| Patrón | Problema que Resuelve | Prioridad | Complejidad |
|--------|----------------------|-----------|-------------|
| **Domain Events** | Acoplamiento entre módulos | ⭐⭐⭐⭐⭐ Alta | Media |
| **Value Objects** | Validación dispersa, lógica de negocio | ⭐⭐⭐⭐ Alta | Baja |
| **CQRS** | Queries lentas, escalabilidad | ⭐⭐⭐⭐ Alta | Media |
| **Unit of Work** | Transacciones complejas | ⭐⭐⭐ Media | Media |
| **Specification** | Queries complejas reutilizables | ⭐⭐⭐ Media | Media |
| **DI Simplificado** | Mantenibilidad, boilerplate | ⭐⭐⭐⭐ Alta | Baja |

---

## 4. Plan de Migración

### 4.1 Estrategia General

**Enfoque:** **Migración Incremental** (Strangler Fig Pattern)
- No reescribir todo de una vez
- Migrar módulo por módulo
- Mantener compatibilidad hacia atrás
- Agregar nuevos módulos con nueva arquitectura
- Refactorizar módulos existentes gradualmente

### 4.2 Fases de Migración

#### FASE 0: Preparación (1 semana)

**Objetivo**: Establecer fundamentos sin romper nada.

##### Tareas:
1. **Crear estructura shared mejorada** (2 días)
   ```bash
   # Crear nuevas carpetas
   mkdir -p src/shared/domain/{events,specifications,value_objects}
   mkdir -p src/shared/app/{commands,queries,handlers}
   mkdir -p src/shared/infra/{events,buses,di}
   ```

2. **Implementar bases genéricas** (2 días)
   - `src/shared/domain/events.py` - DomainEvent base
   - `src/shared/domain/value_objects.py` - ValueObject base + Money, Email, etc.
   - `src/shared/domain/specifications.py` - Specification base
   - `src/shared/app/commands.py` - Command base
   - `src/shared/app/queries.py` - Query base
   - `src/shared/app/handlers.py` - CommandHandler, QueryHandler
   - `src/shared/app/unit_of_work.py` - UnitOfWork interface
   - `src/shared/infra/events/event_bus.py` - EventBus
   - `src/shared/infra/unit_of_work.py` - SQLAlchemyUnitOfWork

3. **Implementar decoradores DI** (1 día)
   - `src/shared/infra/di/decorators.py` - @singleton, @scoped, @transient

4. **Tests unitarios para bases** (2 días)
   - Test EventBus
   - Test Value Objects
   - Test Specifications
   - Test UnitOfWork

**Entregables:**
- ✅ Nuevas clases base implementadas
- ✅ Tests pasando
- ✅ Documentación de patrones
- ⚠️ Sin romper código existente (coexistencia)

---

#### FASE 1: Migrar Módulo Piloto - Customers (2 semanas)

**Objetivo**: Migrar un módulo completo como prueba de concepto.

**¿Por qué Customers?**
- Módulo relativamente simple
- No tiene dependencias complejas
- Permite probar todos los patrones

##### Semana 1: Refactorizar Customer con Value Objects y Commands

1. **Introducir Value Objects** (2 días)
   ```python
   # src/customers/domain/entities.py (ANTES)
   @dataclass
   class Customer(Entity):
       name: str
       tax_id: str           # ❌ Primitivo
       email: str            # ❌ Primitivo
       phone: str            # ❌ Primitivo
       credit_limit: float   # ❌ Primitivo

   # src/customers/domain/entities.py (DESPUÉS)
   @dataclass
   class Customer(Entity):
       name: str
       tax_id: TaxId         # ✅ Value Object
       email: Email          # ✅ Value Object
       phone: PhoneNumber    # ✅ Value Object
       credit_limit: Money   # ✅ Value Object

       def has_available_credit(self, amount: Money) -> bool:
           return self.credit_limit >= amount
   ```

2. **Convertir Use Cases a Command Handlers** (2 días)
   ```python
   # src/customers/app/commands/create_customer.py
   @dataclass
   class CreateCustomerCommand(Command):
       name: str
       tax_id: str
       email: str
       # ...

   @scoped
   class CreateCustomerCommandHandler(CommandHandler[CreateCustomerCommand, CustomerResponse]):
       def __init__(self, customer_repo: Repository[Customer]):
           self.customer_repo = customer_repo

       def handle(self, command: CreateCustomerCommand) -> CustomerResponse:
           # Validar y crear value objects
           customer = Customer(
               name=command.name,
               tax_id=TaxId(command.tax_id, "EC"),
               email=Email(command.email),
               # ...
           )
           customer = self.customer_repo.create(customer)
           return CustomerResponse.from_entity(customer)
   ```

3. **Adaptar Controllers** (1 día)
   ```python
   # src/customers/infra/controllers.py
   class CustomerController:
       def __init__(self, create_handler: CreateCustomerCommandHandler):
           self.create_handler = create_handler

       def create(self, request: CreateCustomerRequest) -> CustomerResponse:
           command = CreateCustomerCommand(**request.dict())
           return self.create_handler.handle(command)
   ```

##### Semana 2: Domain Events y Tests

4. **Agregar Domain Events** (2 días)
   ```python
   # src/customers/domain/events.py
   @dataclass
   class CustomerCreated(DomainEvent):
       customer_id: int
       name: str
       email: str

   # src/customers/app/commands/create_customer.py
   def handle(self, command: CreateCustomerCommand) -> CustomerResponse:
       customer = Customer(...)
       customer = self.customer_repo.create(customer)

       # Emit event
       EventBus.publish(CustomerCreated(
           aggregate_id=customer.id,
           customer_id=customer.id,
           name=customer.name,
           email=str(customer.email)
       ))

       return CustomerResponse.from_entity(customer)
   ```

5. **Implementar Specifications** (1 día)
   ```python
   # src/customers/domain/specifications.py
   class ActiveCustomers(Specification):
       def to_sql_criteria(self):
           return [CustomerModel.is_active == True]

   class CustomerWithCreditLimit(Specification):
       def __init__(self, min_limit: Money):
           self.min_limit = min_limit

       def to_sql_criteria(self):
           return [CustomerModel.credit_limit >= self.min_limit.amount]
   ```

6. **Tests completos** (2 días)
   - Tests unitarios de Value Objects
   - Tests de Command Handlers (mock repositories)
   - Tests de Events (mock EventBus)
   - Tests de Specifications
   - Tests de integración (API endpoints)

**Entregables:**
- ✅ Customers migrado a nueva arquitectura
- ✅ Cobertura de tests >80%
- ✅ Documentación de patterns usados
- ✅ Código legacy todavía funciona

---

#### FASE 2: Implementar Sales con CQRS y UoW (3 semanas)

**Objetivo**: Crear módulo Sales desde cero con arquitectura completa.

##### Semana 1: Dominio y Comandos

1. **Diseñar Dominio** (2 días)
   ```python
   # src/sales/domain/entities.py
   @dataclass
   class Sale(Entity):
       customer_id: int
       warehouse_id: int
       sale_date: datetime
       status: SaleStatus
       items: List[SaleItem]

       @property
       def subtotal(self) -> Money:
           return sum((item.subtotal for item in self.items), Money(Decimal('0')))

       @property
       def total(self) -> Money:
           return self.subtotal + self.tax - self.discount

       def add_item(self, item: SaleItem) -> None:
           if self.status != SaleStatus.DRAFT:
               raise BusinessRuleViolation("Cannot modify confirmed sale")
           self.items.append(item)

       def confirm(self) -> None:
           if self.status != SaleStatus.DRAFT:
               raise BusinessRuleViolation("Only drafts can be confirmed")
           self.status = SaleStatus.CONFIRMED

   @dataclass
   class SaleItem:
       product_id: int
       quantity: int
       unit_price: Money
       discount: Percentage

       @property
       def subtotal(self) -> Money:
           base = self.unit_price * self.quantity
           return base - self.discount.apply_to(base)
   ```

2. **Implementar Commands** (2 días)
   - CreateSaleCommand + Handler
   - AddSaleItemCommand + Handler
   - ConfirmSaleCommand + Handler (con UoW)
   - CancelSaleCommand + Handler
   - RegisterPaymentCommand + Handler

3. **Domain Events** (1 día)
   - SaleCreated
   - SaleItemAdded
   - SaleConfirmed
   - SaleCancelled
   - PaymentReceived

##### Semana 2: Integración con Inventory (via Events)

4. **Event Handlers en Inventory** (2 días)
   ```python
   # src/inventory/infra/event_handlers.py
   @event_handler(SaleConfirmed)
   def handle_sale_confirmed(event: SaleConfirmed):
       with uow_factory() as uow:
           for item in event.items:
               # Validate stock
               stock = uow.stocks.first(
                   product_id=item['product_id'],
                   warehouse_id=event.warehouse_id
               )
               if not stock or stock.quantity < item['quantity']:
                   raise InsufficientStockError(...)

               # Create movement
               movement = Movement(
                   product_id=item['product_id'],
                   warehouse_id=event.warehouse_id,
                   type=MovementType.OUT,
                   quantity=item['quantity'],
                   reference_type='SALE',
                   reference_id=event.sale_id
               )
               uow.movements.create(movement)

               # Update stock
               stock.quantity -= item['quantity']
               uow.stocks.update(stock)

           uow.commit()
   ```

5. **Implementar Unit of Work en ConfirmSale** (1 día)
   ```python
   # src/sales/app/commands/confirm_sale.py
   def handle(self, command: ConfirmSaleCommand) -> SaleResponse:
       with self.uow_factory() as uow:
           sale = uow.sales.get_by_id(command.sale_id)
           sale.confirm()
           sale = uow.sales.update(sale)
           uow.commit()

           # Emit event AFTER commit
           EventBus.publish(SaleConfirmed(...))

           return SaleResponse.from_entity(sale)
   ```

6. **Tests de integración Sales ↔ Inventory** (2 días)
   - Test: Confirmar venta reduce stock
   - Test: Cancelar venta incrementa stock
   - Test: Venta sin stock falla
   - Test: Transacción rollback funciona

##### Semana 3: CQRS y Queries Optimizadas

7. **Implementar Query Handlers** (2 días)
   ```python
   # src/sales/infra/queries/sales_report_query.py
   @scoped
   class GetSalesReportQueryHandler(QueryHandler[GetSalesReportQuery, SalesReportResponse]):
       def __init__(self, session: Session):
           self.session = session

       def handle(self, query: GetSalesReportQuery) -> SalesReportResponse:
           # Raw SQL for performance
           sql = text("""
               SELECT
                   DATE(s.sale_date) as date,
                   COUNT(s.id) as total_sales,
                   SUM(s.total) as revenue,
                   AVG(s.total) as avg_sale
               FROM sales s
               WHERE s.sale_date BETWEEN :start_date AND :end_date
                   AND s.status = 'CONFIRMED'
               GROUP BY DATE(s.sale_date)
               ORDER BY date DESC
           """)
           # ...
   ```

8. **Implementar más Queries** (2 días)
   - GetSalesByCustomerQuery
   - GetTopSellingProductsQuery
   - GetPendingPaymentsQuery

9. **Controllers y Routes** (1 día)

**Entregables:**
- ✅ Módulo Sales completo con nueva arquitectura
- ✅ Integración con Inventory via eventos
- ✅ CQRS implementado
- ✅ Tests de integración pasando

---

#### FASE 3: Migrar Inventory a Event-Driven (2 semanas)

**Objetivo**: Refactorizar inventory para usar eventos en lugar de acoplamiento directo.

##### Tareas:

1. **Extraer lógica de stock a Event Handlers** (3 días)
   - Actualmente: `CreateMovementUseCase` modifica stock directamente
   - Nuevo: `CreateMovementCommandHandler` emite `MovementCreated` event
   - `StockEventHandler` escucha `MovementCreated` y actualiza stock

2. **Implementar Commands y Queries** (3 días)
   - CreateMovementCommand
   - GetStockByProductQuery
   - GetLowStockQuery

3. **Agregar Specifications** (2 días)
   - LowStockSpecification
   - StockInWarehouseSpecification

4. **Refactorizar con UnitOfWork** (2 días)

5. **Tests** (2 días)

**Entregables:**
- ✅ Inventory desacoplado
- ✅ Event-driven
- ✅ Tests actualizados

---

#### FASE 4: Migrar Catalog (1 semana)

**Objetivo**: Migrar products y categories a nueva arquitectura.

##### Tareas similares:
1. Value Objects (ProductName, SKU, Price)
2. Commands (CreateProduct, UpdateProduct)
3. Queries (SearchProducts con Specifications)
4. Events (ProductCreated, ProductPriceChanged)
5. Tests

---

#### FASE 5: Simplificar DI Container (1 semana)

**Objetivo**: Eliminar registro manual, usar decoradores.

##### Tareas:

1. **Aplicar decoradores a todos los componentes** (3 días)
   ```python
   # Antes
   container.register(
       Repository[Product],
       factory=lambda c, scope_id: ProductRepositoryImpl(...),
       scope=LifetimeScope.SCOPED
   )

   # Después
   @repository(Product)
   class ProductRepositoryImpl(BaseRepository[Product]):
       pass
   ```

2. **Eliminar init_* functions en src/__init__.py** (1 día)

3. **Tests** (1 día)

4. **Documentación** (1 día)

**Entregables:**
- ✅ src/__init__.py reducido de 629 a <100 líneas
- ✅ Todos los módulos con decoradores
- ✅ Auto-discovery funcionando

---

#### FASE 6: Implementar Módulos Nuevos (según ROADMAP)

**Módulos futuros** (ya con arquitectura nueva):
- **Suppliers** (2 semanas)
- **Purchases** (3 semanas)
- **Pricing** (2 semanas)
- **Warehouse** (multi-almacén) (2 semanas)
- **Reporting** (CQRS completo) (2 semanas)
- **Accounting** (3 semanas)

Cada uno siguiendo el template:
```
module/
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   ├── events.py
│   ├── specifications.py
│   └── exceptions.py
├── app/
│   ├── commands/
│   └── queries/
└── infra/
    ├── models.py
    ├── mappers.py
    ├── repositories.py
    ├── controllers.py
    ├── routes.py
    ├── validators.py
    └── event_handlers.py
```

---

### 4.3 Cronograma Completo

| Fase | Duración | Descripción | Entregables |
|------|----------|-------------|-------------|
| **Fase 0** | 1 semana | Preparación - Bases genéricas | Clases base, EventBus, decorators |
| **Fase 1** | 2 semanas | Migrar Customers (piloto) | Customers con nueva arquitectura |
| **Fase 2** | 3 semanas | Implementar Sales (CQRS + UoW) | Sales completo, integrado con inventory |
| **Fase 3** | 2 semanas | Migrar Inventory (event-driven) | Inventory desacoplado |
| **Fase 4** | 1 semana | Migrar Catalog | Catalog con nueva arquitectura |
| **Fase 5** | 1 semana | Simplificar DI | DI auto-discovery |
| **TOTAL** | **10 semanas** | **Arquitectura base completamente migrada** | **Sistema robusto y escalable** |

**Después**:
- Fase 6+: Implementar nuevos módulos (Suppliers, Purchases, etc.) según ROADMAP

---

### 4.4 Estrategia de Testing Durante Migración

#### 4.4.1 Tests a Mantener
- ✅ Tests existentes siguen pasando
- ✅ Cada cambio debe tener tests

#### 4.4.2 Tests Nuevos
- Unit tests para Value Objects
- Unit tests para Specifications
- Unit tests para Command Handlers (mock repos)
- Integration tests para Event Handlers
- Integration tests para CQRS Queries
- E2E tests para flujos críticos

#### 4.4.3 Coverage Goal
- >80% para módulos nuevos
- >70% para módulos migrados

---

### 4.5 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Romper funcionalidad existente** | Media | Alto | Tests exhaustivos, migración incremental |
| **Aumentar complejidad** | Media | Medio | Documentación clara, templates, ejemplos |
| **Curva de aprendizaje del equipo** | Alta | Medio | Capacitación, pair programming, code reviews |
| **Performance degradation** | Baja | Alto | Benchmarks antes/después, profiling |
| **Scope creep** | Alta | Alto | Fases claras, no agregar features en migración |
| **Eventos perdidos** | Baja | Alto | Event logging, monitoring, retry mechanisms |

---

## 5. Conclusiones y Recomendaciones

### 5.1 Resumen Ejecutivo

**La arquitectura actual es BUENA para el estado actual del proyecto**, pero necesita evolucionar para soportar el crecimiento planificado (ventas, POS, contabilidad).

**Principales problemas a resolver:**
1. **Acoplamiento** entre módulos (sin eventos)
2. **Mantenibilidad** (DI verboso)
3. **Escalabilidad** (sin CQRS para queries complejas)
4. **Lógica de negocio dispersa** (sin Value Objects)

**Solución propuesta:**
- Migración incremental (10 semanas para base)
- Patrones modernos (DDD, Event-Driven, CQRS)
- Mantener compatibilidad durante migración
- Nuevos módulos con arquitectura mejorada

### 5.2 Beneficios Esperados

#### 5.2.1 Corto Plazo (Fases 0-2, ~6 semanas)
- ✅ Módulo Sales implementado (crítico para negocio)
- ✅ Desacoplamiento sales ↔ inventory
- ✅ Value Objects con validación robusta
- ✅ Menos bugs de validación

#### 5.2.2 Mediano Plazo (Fases 3-5, ~4 semanas)
- ✅ Todos los módulos existentes migrados
- ✅ DI simplificado (90% menos código)
- ✅ Event-driven architecture funcionando
- ✅ Base sólida para nuevos módulos

#### 5.2.3 Largo Plazo (Fase 6+, meses)
- ✅ Sistema escalable (CQRS, eventos)
- ✅ Fácil agregar módulos (Purchases, Pricing, etc.)
- ✅ Performance optimizado (queries dedicadas)
- ✅ Auditoría completa (event store)
- ✅ Fácil agregar integraciones (webhooks, APIs externas)

### 5.3 Métricas de Éxito

| Métrica | Antes | Meta Después | Medición |
|---------|-------|--------------|----------|
| **Líneas en src/__init__.py** | 629 | <100 | Conteo líneas |
| **Tiempo agregar use case** | 10 min | 2 min | Cronómetro |
| **Acoplamiento entre módulos** | Alto (directo) | Bajo (eventos) | Dependency graph |
| **Cobertura de tests** | ~60% | >80% | pytest --cov |
| **Query performance (reportes)** | N/A | <500ms | Profiling |
| **Tiempo onboarding desarrollador** | 2 días | 4 horas | Encuesta |

### 5.4 Recomendaciones Priorizadas

#### ⭐⭐⭐⭐⭐ CRÍTICO (Hacer primero)
1. **Implementar Domain Events** (Fase 0)
   - Desacopla módulos
   - Permite implementar Sales sin tocar Inventory
   - Facilita auditoría

2. **Implementar Sales Module** (Fase 2)
   - Crítico para el negocio
   - Usa nueva arquitectura desde cero
   - Prueba de concepto de patrones

3. **Value Objects** (Fase 1)
   - Valida datos desde dominio
   - Previene bugs
   - Fácil de implementar

#### ⭐⭐⭐⭐ IMPORTANTE (Hacer pronto)
4. **CQRS para Reportes** (Fase 2)
   - Queries optimizadas
   - Escalabilidad
   - Performance

5. **Simplificar DI** (Fase 5)
   - Reduce mantenimiento
   - Menos errores
   - Mejor developer experience

#### ⭐⭐⭐ DESEABLE (Hacer después)
6. **Specification Pattern** (Fase 3-4)
   - Queries reutilizables
   - Código más limpio

7. **Unit of Work explícito** (Fase 2-3)
   - Transacciones más claras
   - Testing más fácil

### 5.5 Consideraciones Adicionales

#### 5.5.1 Equipo
- **Capacitación**: 1 semana de workshops sobre DDD, eventos, CQRS
- **Pair Programming**: Primeras implementaciones en pair
- **Code Reviews**: Obligatorias para patrones nuevos

#### 5.5.2 Herramientas
- **Event Monitoring**: Agregar logging de eventos
- **Performance Monitoring**: APM (New Relic, DataDog, etc.)
- **Documentation**: Usar MkDocs para documentar arquitectura

#### 5.5.3 Futuro
- **Event Sourcing** (opcional): Para auditoría completa (contabilidad)
- **Async Events**: Con Celery/RabbitMQ para procesos lentos
- **API Gateway**: Para exponer servicios a frontend/mobile
- **Microservices** (muy futuro): Si escala mucho, separar bounded contexts

### 5.6 Conclusión Final

> **La arquitectura actual tiene buenas bases**, pero necesita evolucionar para soportar un sistema empresarial completo.
>
> **Con la migración propuesta (10 semanas)**:
> - Sistema desacoplado y escalable
> - Fácil agregar nuevos módulos
> - Performance optimizado
> - Mantenimiento reducido en 70%
>
> **Recomendación**: **Ejecutar el plan de migración por fases**, comenzando con las Fases 0-2 (implementar Sales con nueva arquitectura) para validar la propuesta antes de comprometer recursos a la migración completa.

---

## Apéndices

### A. Glosario de Términos

- **Bounded Context**: Límite explícito dentro del cual un modelo de dominio es válido
- **CQRS**: Command Query Responsibility Segregation - separar comandos (write) de queries (read)
- **Domain Event**: Evento que representa algo que pasó en el dominio
- **DDD**: Domain-Driven Design - diseño guiado por el dominio
- **Specification**: Patrón para encapsular reglas de negocio como objetos
- **Unit of Work**: Patrón para mantener lista de objetos afectados por transacción
- **Value Object**: Objeto inmutable que representa un concepto del dominio

### B. Referencias

#### Libros
- **Domain-Driven Design** - Eric Evans
- **Implementing Domain-Driven Design** - Vaughn Vernon
- **Clean Architecture** - Robert C. Martin
- **Patterns of Enterprise Application Architecture** - Martin Fowler

#### Artículos
- [CQRS Pattern - Microsoft Docs](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Domain Events - Martin Fowler](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Specification Pattern](https://en.wikipedia.org/wiki/Specification_pattern)

#### Ejemplos de Código
- Ver carpetas de ejemplo en `examples/` (crear)

### C. Templates para Nuevos Módulos

Ver archivo `TEMPLATES.md` (crear) con templates completos para:
- Entity
- Value Object
- Command + Handler
- Query + Handler
- Event + Handler
- Specification
- Repository

---

**Fin del Documento**

---

**Changelog:**
- 2026-02-06: Versión inicial
