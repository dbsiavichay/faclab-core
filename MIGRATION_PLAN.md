# Plan de Migración Arquitectónica - Faclab Core

**Fecha de creación:** 2026-02-06
**Última actualización:** 2026-02-10
**Versión:** 1.1
**Documento de referencia:** ARCHITECTURE_ANALYSIS.md

---

## 📊 Estado Actual de la Migración

| Fase | Estado | Fecha Completada | Commit | Tests |
|------|--------|-----------------|--------|-------|
| **Fase 0: Fundamentos** | ✅ COMPLETADA | 2026-02-09 | 792981b | 16/16 ✅ |
| **Fase 1: Customers (Piloto)** | ✅ COMPLETADA | 2026-02-10 | 06c9bbb | 39/39 ✅ |
| **Fase 2: Sales** | ✅ COMPLETADA | 2026-02-10 | pending | 50/50 ✅ |
| **Fase 3: Inventory** | 🔜 SIGUIENTE | - | - | - |
| **Fase 4: Catalog** | ⏸️ PENDIENTE | - | - | - |
| **Fase 5: Simplificar DI** | ⏸️ PENDIENTE | - | - | - |

**Total de Tests Pasando:** 105/105 ✅

### ✅ Logros Completados
- ✅ Fundamentos arquitectónicos (DomainEvent, EventBus, ValueObjects, Specifications, Commands, Queries, UnitOfWork)
- ✅ Módulo Customers completamente migrado a CQRS
- ✅ **Módulo Sales implementado desde cero con nueva arquitectura**
- ✅ **Integración Sales ↔ Inventory vía eventos funcionando**
- ✅ Patrón de eventos funcionando (EventBus con decoradores)
- ✅ Value Objects validando en comandos (Email, TaxId)
- ✅ Specifications para queries complejas
- ✅ **105 tests unitarios pasando (100% éxito)**

### 🎯 Siguiente Paso Recomendado
**Fase 3: Migrar Inventory a Event-Driven** - Desacoplar CreateMovementUseCase del StockRepository usando eventos.

---

## Contexto del Proyecto (para futuras sesiones de Claude Code)

### Qué es Faclab Core

Sistema de gestión empresarial construido con **FastAPI + SQLAlchemy + PostgreSQL**. Actualmente gestiona catálogo de productos, inventario y clientes. Está planeado para crecer a ventas, compras, proveedores, pricing, multi-almacén, reportes y contabilidad.

### Stack

- Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, Docker

### Estructura actual de archivos

```
src/
├── shared/                  # Kernel compartido
│   ├── domain/
│   │   ├── entities.py     # class Entity (base dataclass, método dict())
│   │   ├── exceptions.py
│   │   └── ports.py        # class Logger (ABC)
│   ├── app/
│   │   └── repositories.py # class Repository(Generic[T], ABC) — CRUD interface
│   └── infra/
│       ├── di.py           # DependencyContainer con LifetimeScope (SINGLETON/SCOPED/TRANSIENT)
│       ├── db.py           # SQLAlchemy Base y session factory
│       ├── repositories.py # BaseRepository(Repository[E]) — implementación genérica CRUD
│       ├── mappers.py      # class Mapper(Generic[E, M], ABC) — to_entity/to_dict
│       ├── middlewares.py   # ErrorHandlingMiddleware
│       ├── exceptions.py   # NotFoundException, etc.
│       └── validators.py   # Base Pydantic validators
├── catalog/
│   └── product/
│       ├── domain/entities.py      # Product(Entity), Category(Entity)
│       ├── app/use_cases/          # CreateProductUseCase, UpdateProductUseCase, etc.
│       │   ├── product.py          # 5 use cases: Create, Update, Delete, GetById, GetAll
│       │   └── category.py         # 5 use cases: Create, Update, Delete, GetById, GetAll
│       ├── app/types.py            # TypedDicts para input/output
│       └── infra/
│           ├── models.py           # ProductModel, CategoryModel (SQLAlchemy)
│           ├── mappers.py          # ProductMapper, CategoryMapper
│           ├── repositories.py     # ProductRepositoryImpl, CategoryRepositoryImpl
│           ├── controllers.py      # ProductController, CategoryController
│           ├── routes.py           # ProductRouter, CategoryRouter (FastAPI APIRouter)
│           └── validators.py       # Pydantic schemas (ProductInput, ProductResponse, etc.)
├── inventory/
│   ├── stock/
│   │   ├── domain/entities.py      # Stock(Entity) — con update_quantity()
│   │   ├── app/use_cases.py        # FilterStocksUseCase
│   │   └── infra/                  # models, mappers, repos, controllers, routes, validators
│   └── movement/
│       ├── domain/
│       │   ├── entities.py         # Movement(Entity)
│       │   ├── constants.py        # MovementType enum (IN/OUT)
│       │   └── exceptions.py
│       ├── app/use_cases.py        # CreateMovementUseCase, FilterMovementsUseCase
│       └── infra/                  # models, mappers, repos, controllers, routes, validators
└── customers/
    ├── domain/entities.py          # Customer(Entity), CustomerContact(Entity)
    ├── app/use_cases/
    │   ├── customer.py             # Create, Update, Delete, GetAll, GetById, GetByTaxId, Activate, Deactivate
    │   └── customer_contact.py     # Create, Update, Delete, GetById, GetByCustomerId
    └── infra/                      # models, mappers, repos, controllers, routes, validators
```

### Flujo actual de un request

```
HTTP Request
  → FastAPI Route (infra/routes.py)
    → Controller (injected via DI, infra/controllers.py)
      → Use Case (injected, app/use_cases/)
        → Repository interface (app/repositories.py)
          → BaseRepository impl (infra/repositories.py)
            → Mapper (to_entity/to_dict)
              → SQLAlchemy Model → PostgreSQL
```

### Cómo funciona el DI actual

Todo el registro está en `src/__init__.py` (629 líneas). Ejemplo del patrón repetitivo:

```python
# Mapper (SINGLETON)
container.register(ProductMapper, factory=lambda c: ProductMapper(), scope=LifetimeScope.SINGLETON)

# Repository (SCOPED — comparte session por request)
container.register(
    Repository[Product],
    factory=lambda c, scope_id=None: ProductRepositoryImpl(
        c.get_scoped_db_session(scope_id) if scope_id else c.get_db_session(),
        c.resolve(ProductMapper),
    ),
    scope=LifetimeScope.SCOPED,
)

# Use Case (SCOPED)
container.register(
    CreateProductUseCase,
    factory=lambda c, scope_id=None: CreateProductUseCase(
        c.resolve_scoped(Repository[Product], scope_id)
        if scope_id else c.resolve(Repository[Product])
    ),
    scope=LifetimeScope.SCOPED,
)

# Controller (SCOPED)
container.register(
    ProductController,
    factory=lambda c, scope_id=None: ProductController(
        c.resolve_scoped(CreateProductUseCase, scope_id) if scope_id else c.resolve(CreateProductUseCase),
        c.resolve_scoped(UpdateProductUseCase, scope_id) if scope_id else c.resolve(UpdateProductUseCase),
        # ... 5 use cases
    ),
    scope=LifetimeScope.SCOPED,
)

# Dependency function para FastAPI (generator que cierra scope)
def get_product_controller(scope_id: str = Depends(get_request_scope_id)) -> ProductController:
    controller = container.resolve_scoped(ProductController, scope_id)
    try:
        yield controller
    finally:
        container.close_scope(scope_id)
```

**Punto clave**: Cada scope_id (UUID) identifica un request. Dentro del mismo scope, todas las dependencias SCOPED comparten la misma session de DB.

### Cómo funciona un Use Case actual

```python
class CreateProductUseCase:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def execute(self, product_create: ProductInput) -> ProductOutput:
        product = Product(**product_create)       # dict → entity
        product = self.repo.create(product)        # persist
        return product.dict()                      # entity → dict
```

**Patrón**: recibe TypedDict (input), crea Entity, opera con Repository, retorna dict (output). El Controller luego valida el dict con Pydantic (`ProductResponse.model_validate(dict)`).

### Acoplamiento actual entre módulos

El ejemplo más relevante — `CreateMovementUseCase` depende directamente de `Repository[Stock]`:

```python
class CreateMovementUseCase:
    def __init__(self, movement_repo: Repository[Movement], stock_repo: Repository[Stock]):
        self.movement_repo = movement_repo
        self.stock_repo = stock_repo

    def execute(self, movement_create):
        movement = self.movement_repo.create(movement)
        stock = self.stock_repo.first(product_id=movement.product_id)
        if stock is None:
            stock = Stock(product_id=movement.product_id, quantity=movement.quantity)
            self.stock_repo.create(stock)
        else:
            stock.update_quantity(movement.quantity)
            self.stock_repo.update(stock)
        return movement.dict()
```

**Problema**: Si sales quiere crear movimientos, necesitará conocer inventory directamente. Esto se multiplica con cada módulo nuevo.

### Problemas diagnosticados (resumen)

| Problema | Impacto | Ejemplo concreto |
|----------|---------|-----------------|
| **DI verboso** | 629 líneas, cada use case nuevo = 8-10 líneas de registro | `src/__init__.py` |
| **Sin Domain Events** | Acoplamiento directo entre módulos | movement → stock directo |
| **Sin Value Objects** | Validación dispersa, tipos primitivos sin garantías | `tax_id: str` sin validar formato |
| **Sin CQRS** | No se puede optimizar queries para reportes | Same model read/write |
| **Sin Unit of Work** | Cada repo.create() hace commit inmediato, sin atomicidad | 2 commits separados en CreateMovement |
| **Sin Specifications** | Queries complejas no reutilizables | Filtros hardcodeados en repos |
| **BaseRepository usa .get()** | Deprecated en SQLAlchemy 2.0 | `session.query(Model).get(id)` |

---

## Plan de Migración

### Estrategia: Migración Incremental (Strangler Fig)

- NO reescribir todo de golpe
- Agregar nuevas abstracciones al lado del código existente
- Migrar módulo por módulo
- Los módulos nuevos (sales, purchases) nacen con la nueva arquitectura
- Los módulos existentes se refactorizan gradualmente

---

### FASE 0: Crear Fundamentos (1 semana) ✅ COMPLETADA

**Estado**: ✅ **COMPLETADA** - 2026-02-09 (commit 792981b)
**Objetivo**: Implementar las clases base sin romper nada existente.

#### Tarea 0.1: Crear Domain Events base (1 día)

Crear `src/shared/domain/events.py`:

```python
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

@dataclass
class DomainEvent(ABC):
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
        return {}
```

#### Tarea 0.2: Crear EventBus (1 día)

Crear `src/shared/infra/events/__init__.py` y `src/shared/infra/events/event_bus.py`:

```python
from typing import Callable, Dict, List, Type
from src.shared.domain.events import DomainEvent
import logging

logger = logging.getLogger(__name__)

class EventBus:
    _handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        event_type = type(event)
        if event_type in cls._handlers:
            for handler in cls._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in handler {handler.__name__} for {event_type.__name__}: {e}")

    @classmethod
    def clear(cls) -> None:
        cls._handlers.clear()
```

Crear `src/shared/infra/events/decorators.py`:

```python
from typing import Type, Callable
from src.shared.domain.events import DomainEvent
from src.shared.infra.events.event_bus import EventBus

def event_handler(event_type: Type[DomainEvent]) -> Callable:
    def decorator(func: Callable) -> Callable:
        EventBus.subscribe(event_type, func)
        return func
    return decorator
```

#### Tarea 0.3: Crear Value Objects base (1 día)

Crear `src/shared/domain/value_objects.py`:

```python
from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
import re

@dataclass(frozen=True)
class ValueObject(ABC):
    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        pass

@dataclass(frozen=True)
class Money(ValueObject):
    amount: Decimal
    currency: str = "USD"

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

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

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def _validate(self) -> None:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class TaxId(ValueObject):
    value: str
    country: str = "EC"

    def _validate(self) -> None:
        if self.country == "EC":
            if not re.match(r'^\d{13}$', self.value):
                raise ValueError(f"Invalid Ecuadorian RUC: {self.value}. Must be 13 digits.")

    def formatted(self) -> str:
        if self.country == "EC":
            return f"{self.value[:3]}-{self.value[3:10]}-{self.value[10:]}"
        return self.value

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class Percentage(ValueObject):
    value: Decimal

    def _validate(self) -> None:
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        if not 0 <= self.value <= 100:
            raise ValueError(f"Percentage must be between 0 and 100, got {self.value}")

    def as_decimal(self) -> Decimal:
        return self.value / Decimal('100')

    def apply_to(self, amount: Money) -> Money:
        return amount * float(self.as_decimal())
```

#### Tarea 0.4: Crear Command/Query base (1 día)

Crear `src/shared/app/commands.py`:

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

@dataclass
class Command(ABC):
    pass

TCommand = TypeVar('TCommand', bound=Command)
TResult = TypeVar('TResult')

class CommandHandler(Generic[TCommand, TResult], ABC):
    @abstractmethod
    def handle(self, command: TCommand) -> TResult:
        pass
```

Crear `src/shared/app/queries.py`:

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

@dataclass
class Query(ABC):
    pass

TQuery = TypeVar('TQuery', bound=Query)
TResult = TypeVar('TResult')

class QueryHandler(Generic[TQuery, TResult], ABC):
    @abstractmethod
    def handle(self, query: TQuery) -> TResult:
        pass
```

#### Tarea 0.5: Crear Unit of Work interface e implementación (1 día)

Crear `src/shared/app/unit_of_work.py`:

```python
from abc import ABC, abstractmethod

class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self): pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): pass

    @abstractmethod
    def commit(self) -> None: pass

    @abstractmethod
    def rollback(self) -> None: pass
```

Crear `src/shared/infra/unit_of_work.py`:

```python
from typing import Optional
from sqlalchemy.orm import Session
from src.shared.app.unit_of_work import UnitOfWork

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
```

#### Tarea 0.6: Crear Specification base (0.5 día)

Crear `src/shared/domain/specifications.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Any

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool: pass

    @abstractmethod
    def to_sql_criteria(self) -> List[Any]: pass

    def __and__(self, other: 'Specification') -> 'AndSpecification':
        return AndSpecification(self, other)

    def __or__(self, other: 'Specification') -> 'OrSpecification':
        return OrSpecification(self, other)

    def __invert__(self) -> 'NotSpecification':
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def to_sql_criteria(self) -> List[Any]:
        return [*self.left.to_sql_criteria(), *self.right.to_sql_criteria()]

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

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

#### Tarea 0.7: Tests para bases (1 día)

Escribir tests unitarios para:
- EventBus: subscribe, publish, clear, error handling
- Value Objects: Money (arithmetic, validation), Email (validation), TaxId (format)
- Specifications: and, or, not composition
- UnitOfWork: commit, rollback, context manager

#### Tarea 0.8: Agregar filter_by_spec a BaseRepository (0.5 día)

Editar `src/shared/infra/repositories.py` para agregar:

```python
def filter_by_spec(self, spec, order_by=None, desc_order=False, limit=None, offset=None):
    criteria = spec.to_sql_criteria()
    return self.filter(criteria, order_by, desc_order, limit, offset)

def count_by_spec(self, spec) -> int:
    criteria = spec.to_sql_criteria()
    return self.session.query(self.__model__).filter(*criteria).count()
```

**Checklist Fase 0:**
- [x] `src/shared/domain/events.py`
- [x] `src/shared/domain/value_objects.py`
- [x] `src/shared/domain/specifications.py`
- [x] `src/shared/app/commands.py`
- [x] `src/shared/app/queries.py`
- [x] `src/shared/app/unit_of_work.py`
- [x] `src/shared/infra/events/event_bus.py`
- [x] `src/shared/infra/events/decorators.py`
- [x] `src/shared/infra/unit_of_work.py`
- [x] `src/shared/infra/repositories.py` (agregar filter_by_spec)
- [x] Tests unitarios para todo lo anterior (16 tests pasando)
- [x] Código existente sigue funcionando sin cambios

---

### FASE 1: Migrar Customers como piloto (2 semanas) ✅ COMPLETADA

**Estado**: ✅ **COMPLETADA** - 2026-02-10 (commit 06c9bbb)
**Objetivo**: Probar toda la nueva arquitectura con un módulo real.

**Por qué Customers**: Es el módulo más simple, sin dependencias cross-module.

#### Semana 1: Value Objects y Commands

##### Tarea 1.1: Introducir Value Objects en Customer entity (1 día)

Cambiar `src/customers/domain/entities.py`:

**Antes:**
```python
@dataclass
class Customer(Entity):
    name: str
    tax_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    # ...
```

**Después:**
```python
@dataclass
class Customer(Entity):
    name: str
    tax_id: str                    # Mantener str por ahora en entity
    email: Optional[str] = None
    phone: Optional[str] = None
    # ...

    # Agregar métodos de dominio
    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
```

**Nota**: Introducir Value Objects gradualmente. Primero en Command Handlers (validación de entrada), después migrar entity internamente.

##### Tarea 1.2: Convertir Use Cases a Command Handlers (2 días)

Crear `src/customers/app/commands/` con los handlers. Ejemplo:

```python
# src/customers/app/commands/create_customer.py
from dataclasses import dataclass
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.customers.domain.entities import Customer

@dataclass
class CreateCustomerCommand(Command):
    name: str
    tax_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[int] = None

class CreateCustomerCommandHandler(CommandHandler):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def handle(self, command: CreateCustomerCommand) -> dict:
        # Validar con Value Objects
        if command.email:
            Email(command.email)  # Valida o lanza ValueError
        if command.tax_id:
            TaxId(command.tax_id)  # Valida o lanza ValueError

        customer = Customer(
            name=command.name,
            tax_id=command.tax_id,
            email=command.email,
            phone=command.phone,
            address=command.address,
            customer_type=command.customer_type,
            credit_limit=command.credit_limit,
            payment_terms=command.payment_terms,
        )
        customer = self.repo.create(customer)
        return customer.dict()
```

**Mantener** los Use Cases actuales funcionando (backwards compatible). Los Commands son la nueva interfaz; el Controller puede usar Commands internamente.

##### Tarea 1.3: Crear Query Handlers para Customers (1 día)

```python
# src/customers/app/queries/get_customers.py
from dataclasses import dataclass
from src.shared.app.queries import Query, QueryHandler

@dataclass
class GetAllCustomersQuery(Query):
    is_active: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class GetAllCustomersQueryHandler(QueryHandler):
    def __init__(self, repo: Repository[Customer]):
        self.repo = repo

    def handle(self, query: GetAllCustomersQuery) -> list[dict]:
        if query.is_active is not None:
            customers = self.repo.filter_by(
                is_active=query.is_active,
                limit=query.limit,
                offset=query.offset
            )
        else:
            customers = self.repo.get_all()
        return [c.dict() for c in customers]
```

##### Tarea 1.4: Actualizar Controller para usar Commands/Queries (1 día)

```python
# src/customers/infra/controllers.py
class CustomerController:
    def __init__(
        self,
        create_handler: CreateCustomerCommandHandler,
        update_handler: UpdateCustomerCommandHandler,
        delete_handler: DeleteCustomerCommandHandler,
        get_all_handler: GetAllCustomersQueryHandler,
        get_by_id_handler: GetCustomerByIdQueryHandler,
        # ...
    ):
        self.create_handler = create_handler
        # ...

    def create(self, request: CustomerInput) -> CustomerResponse:
        command = CreateCustomerCommand(**request.model_dump(exclude_none=True))
        result = self.create_handler.handle(command)
        return CustomerResponse.model_validate(result)
```

#### Semana 2: Events, Specifications y Tests

##### Tarea 1.5: Agregar Domain Events (1 día)

Crear `src/customers/domain/events.py`:

```python
from dataclasses import dataclass
from src.shared.domain.events import DomainEvent

@dataclass
class CustomerCreated(DomainEvent):
    customer_id: int
    name: str
    tax_id: str

@dataclass
class CustomerDeactivated(DomainEvent):
    customer_id: int
    reason: str = ""
```

Emitir eventos desde los Command Handlers:

```python
# En CreateCustomerCommandHandler.handle():
customer = self.repo.create(customer)
EventBus.publish(CustomerCreated(
    aggregate_id=customer.id,
    customer_id=customer.id,
    name=customer.name,
    tax_id=customer.tax_id
))
```

##### Tarea 1.6: Crear Specifications para Customer (1 día)

```python
# src/customers/domain/specifications.py
from src.shared.domain.specifications import Specification
from src.customers.infra.models import CustomerModel

class ActiveCustomers(Specification):
    def is_satisfied_by(self, customer) -> bool:
        return customer.is_active

    def to_sql_criteria(self):
        return [CustomerModel.is_active == True]

class CustomersByType(Specification):
    def __init__(self, customer_type: str):
        self.customer_type = customer_type

    def is_satisfied_by(self, customer) -> bool:
        return customer.customer_type == self.customer_type

    def to_sql_criteria(self):
        return [CustomerModel.customer_type == self.customer_type]
```

##### Tarea 1.7: Registrar nuevos componentes en DI (1 día)

Agregar los Command/Query handlers al `src/__init__.py` con el mismo patrón actual (registrado manual). NO simplificar el DI todavía — eso es Fase 5.

##### Tarea 1.8: Tests completos (2 días)

- Tests unitarios: Value Objects, Command Handlers (mock repo), Specifications
- Tests de integración: API endpoints siguen funcionando igual

**Checklist Fase 1:**
- [x] `src/customers/app/commands/` — todos los command handlers (8 handlers)
- [x] `src/customers/app/queries/` — todos los query handlers (5 handlers)
- [x] `src/customers/domain/events.py` (CustomerCreated, CustomerUpdated, CustomerActivated, CustomerDeactivated)
- [x] `src/customers/domain/specifications.py` (ActiveCustomers, CustomersByType)
- [x] Controller actualizado para usar commands/queries
- [x] DI registrado para nuevos handlers
- [x] Tests unitarios (39 tests pasando, >80% coverage)
- [x] Tests de integración (endpoints funcionando)
- [x] Use cases completamente reemplazados por handlers

---

### FASE 2: Implementar Sales con arquitectura nueva (3 semanas) ✅ COMPLETADA

**Estado**: ✅ **COMPLETADA** - 2026-02-10
**Objetivo**: Módulo nuevo desde cero con todos los patrones. Este es el módulo más crítico del negocio.

#### Semana 1: Dominio y Commands

##### Tarea 2.1: Diseñar entidades de dominio (1 día)

Crear `src/sales/domain/entities.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from src.shared.domain.entities import Entity

class SaleStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CREDIT = "CREDIT"

@dataclass
class SaleItem(Entity):
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    id: Optional[int] = None

    @property
    def subtotal(self) -> Decimal:
        base = self.unit_price * self.quantity
        return base - (base * self.discount / Decimal("100"))

@dataclass
class Sale(Entity):
    customer_id: int
    status: SaleStatus = SaleStatus.DRAFT
    sale_date: Optional[datetime] = None
    subtotal: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = None
    created_by: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def confirm(self) -> None:
        if self.status != SaleStatus.DRAFT:
            raise ValueError("Only DRAFT sales can be confirmed")
        self.status = SaleStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status not in (SaleStatus.DRAFT, SaleStatus.CONFIRMED):
            raise ValueError("Only DRAFT or CONFIRMED sales can be cancelled")
        self.status = SaleStatus.CANCELLED

@dataclass
class Payment(Entity):
    sale_id: int
    amount: Decimal
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
```

##### Tarea 2.2: Crear Domain Events para Sales (0.5 día)

Crear `src/sales/domain/events.py`:

```python
from dataclasses import dataclass
from typing import List, Dict, Any
from src.shared.domain.events import DomainEvent

@dataclass
class SaleConfirmed(DomainEvent):
    sale_id: int = 0
    customer_id: int = 0
    items: List[Dict[str, Any]] = field(default_factory=list)  # [{product_id, quantity}]
    total: float = 0.0

@dataclass
class SaleCancelled(DomainEvent):
    sale_id: int = 0
    items: List[Dict[str, Any]] = field(default_factory=list)
    reason: str = ""

@dataclass
class PaymentReceived(DomainEvent):
    payment_id: int = 0
    sale_id: int = 0
    amount: float = 0.0
    payment_method: str = ""
```

##### Tarea 2.3: Implementar Command Handlers (3 días)

Crear en `src/sales/app/commands/`:

1. `create_sale.py` — CreateSaleCommand + Handler (crea Sale en DRAFT)
2. `add_sale_item.py` — AddSaleItemCommand + Handler (agrega item, recalcula totales)
3. `remove_sale_item.py` — RemoveSaleItemCommand + Handler
4. `confirm_sale.py` — ConfirmSaleCommand + Handler (**emite SaleConfirmed event**)
5. `cancel_sale.py` — CancelSaleCommand + Handler (**emite SaleCancelled event**)
6. `register_payment.py` — RegisterPaymentCommand + Handler (**emite PaymentReceived event**)

**Reglas de negocio críticas para ConfirmSaleCommand:**
- Validar que sale está en DRAFT
- Validar que tiene items
- Emitir SaleConfirmed (inventory reacciona via event handler)

##### Tarea 2.4: Crear SQLAlchemy models, mappers, repositories (1 día)

`src/sales/infra/models.py`, `mappers.py`, `repositories.py` — siguiendo el patrón existente.

#### Semana 2: Integración con Inventory via Events

##### Tarea 2.5: Crear Event Handlers en Inventory (2 días)

Crear `src/inventory/infra/event_handlers.py`:

```python
from src.sales.domain.events import SaleConfirmed, SaleCancelled
from src.shared.infra.events.decorators import event_handler
from src.inventory.movement.domain.constants import MovementType

@event_handler(SaleConfirmed)
def handle_sale_confirmed(event: SaleConfirmed) -> None:
    """Cuando se confirma una venta, crear movimientos OUT."""
    # Resolver dependencias desde el container
    from src import container
    from src.inventory.movement.app.use_cases import CreateMovementUseCase
    # Usar el use case existente de movement para crear salidas
    for item in event.items:
        movement_uc = container.resolve(CreateMovementUseCase)  # o resolve_scoped
        movement_uc.execute({
            'product_id': item['product_id'],
            'quantity': -item['quantity'],  # OUT = cantidad negativa (depende de lógica actual)
            'type': MovementType.OUT.value,
            'reference_type': 'SALE',
            'reference_id': event.sale_id,
        })

@event_handler(SaleCancelled)
def handle_sale_cancelled(event: SaleCancelled) -> None:
    """Cuando se cancela una venta, revertir con movimientos IN."""
    from src import container
    from src.inventory.movement.app.use_cases import CreateMovementUseCase
    for item in event.items:
        movement_uc = container.resolve(CreateMovementUseCase)
        movement_uc.execute({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'type': MovementType.IN.value,
            'reference_type': 'SALE_CANCELLATION',
            'reference_id': event.sale_id,
        })
```

**Importante**: Los event handlers importan `SaleConfirmed` del domain de sales, pero **no importan nada de infra de sales**. La dependencia es solo en el evento (domain → domain).

##### Tarea 2.6: Registrar event handlers en initialize() (0.5 día)

En `src/__init__.py` agregar al final de `initialize()`:

```python
# Import event handlers to register them via decorators
import src.inventory.infra.event_handlers
```

##### Tarea 2.7: Tests de integración Sales ↔ Inventory (2 días)

Tests críticos:
- Confirmar venta → verifica que se crearon movimientos OUT
- Cancelar venta → verifica que se crearon movimientos IN de reversión
- Confirmar venta sin stock → manejo del error
- Confirmar venta ya confirmada → error de validación

##### Tarea 2.8: Controllers y Routes (1 día)

```
POST   /sales                    # Crear venta (DRAFT)
GET    /sales                    # Listar ventas
GET    /sales/{id}               # Detalle de venta
PUT    /sales/{id}               # Actualizar venta
POST   /sales/{id}/items         # Agregar item
DELETE /sales/{id}/items/{item_id}  # Quitar item
POST   /sales/{id}/confirm       # Confirmar → genera movimiento via evento
POST   /sales/{id}/cancel        # Anular → revierte via evento
POST   /sales/{id}/payments      # Registrar pago
GET    /sales/{id}/payments      # Ver pagos
```

#### Semana 3: CQRS Queries y Migración BD

##### Tarea 2.9: Query Handlers optimizados (2 días)

Crear `src/sales/app/queries/`:

```python
# get_sales_report.py — SQL directo, no usa ORM
class GetSalesReportQueryHandler(QueryHandler):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetSalesReportQuery) -> list:
        sql = text("""
            SELECT DATE(s.sale_date) as date,
                   COUNT(s.id) as total_sales,
                   SUM(s.total) as revenue
            FROM sales s
            WHERE s.sale_date BETWEEN :start AND :end
              AND s.status = 'CONFIRMED'
            GROUP BY DATE(s.sale_date)
            ORDER BY date DESC
        """)
        result = self.session.execute(sql, {'start': query.start_date, 'end': query.end_date})
        return [dict(row._mapping) for row in result]
```

##### Tarea 2.10: Migración de base de datos (1 día)

```bash
make migrations m="create sales, sale_items and payments tables"
make upgrade
```

##### Tarea 2.11: Registrar todo en DI y tests finales (2 días)

**Checklist Fase 2:**
- [x] `src/sales/domain/` — entities, events, exceptions (Sale, SaleItem, Payment + 7 eventos)
- [x] `src/sales/app/commands/` — 6 command handlers (Create, Add/Remove Items, Confirm, Cancel, RegisterPayment)
- [x] `src/sales/app/queries/` — 4 query handlers CQRS (GetAll, GetById, GetItems, GetPayments)
- [x] `src/sales/infra/` — models, mappers, repos, controllers, routes, validators (completo)
- [x] `src/inventory/infra/event_handlers.py` — reacciona a SaleConfirmed/SaleCancelled
- [x] Migración de BD ejecutada (3 tablas: sales, sale_items, payments)
- [x] DI registrado (3 mappers, 3 repos, 10 handlers, 1 controller)
- [x] **50 tests unitarios pasando (100% cobertura)**
- [x] Flujo completo implementado: crear venta → agregar items → confirmar → stock se reduce automáticamente ✨

---

### FASE 3: Migrar Inventory a Event-Driven (2 semanas)

**Objetivo**: Desacoplar la lógica de stock del movement use case.

#### Estado actual del problema

```python
# CreateMovementUseCase ACTUALMENTE hace 2 cosas:
# 1. Crear movement
# 2. Actualizar stock directamente (acoplamiento)
```

#### Solución

1. **CreateMovementUseCase** solo crea el movement y emite `MovementCreated` event
2. **Nuevo StockEventHandler** escucha `MovementCreated` y actualiza stock

##### Tarea 3.1: Crear evento MovementCreated (0.5 día)

```python
# src/inventory/movement/domain/events.py
@dataclass
class MovementCreated(DomainEvent):
    movement_id: int = 0
    product_id: int = 0
    quantity: int = 0
    movement_type: str = ""  # IN o OUT
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
```

##### Tarea 3.2: Refactorizar CreateMovementUseCase (1 día)

**Antes** (acoplado):
```python
class CreateMovementUseCase:
    def __init__(self, movement_repo, stock_repo):
        # ...
    def execute(self, data):
        movement = self.movement_repo.create(...)
        stock = self.stock_repo.first(...)
        stock.update_quantity(...)
        self.stock_repo.update(stock)
```

**Después** (desacoplado):
```python
class CreateMovementUseCase:
    def __init__(self, movement_repo):  # Ya no necesita stock_repo
        self.movement_repo = movement_repo

    def execute(self, data):
        movement = Movement(**data)
        movement = self.movement_repo.create(movement)

        EventBus.publish(MovementCreated(
            aggregate_id=movement.id,
            movement_id=movement.id,
            product_id=movement.product_id,
            quantity=movement.quantity,
            movement_type=movement.type,
        ))
        return movement.dict()
```

##### Tarea 3.3: Crear StockEventHandler (1 día)

```python
# src/inventory/stock/infra/event_handlers.py
@event_handler(MovementCreated)
def handle_movement_created(event: MovementCreated) -> None:
    from src import container
    stock_repo = container.resolve(Repository[Stock])
    stock = stock_repo.first(product_id=event.product_id)
    if stock is None:
        stock = Stock(product_id=event.product_id, quantity=event.quantity)
        stock_repo.create(stock)
    else:
        stock.update_quantity(event.quantity)
        stock_repo.update(stock)
```

##### Tarea 3.4: Convertir a Command Handlers (2 días)

Migrar los use cases restantes de inventory a Commands/Queries.

##### Tarea 3.5: Actualizar DI (movement ya no depende de stock_repo) (0.5 día)

##### Tarea 3.6: Tests (2 días)

- Crear movement → stock se actualiza via evento
- Todo el flujo: venta confirmada → movement creado → stock actualizado

**Checklist Fase 3:**
- [ ] `src/inventory/movement/domain/events.py` — MovementCreated
- [ ] CreateMovementUseCase refactorizado (sin stock_repo)
- [ ] `src/inventory/stock/infra/event_handlers.py` — actualiza stock
- [ ] DI actualizado
- [ ] Tests de integración
- [ ] Cadena completa: SaleConfirmed → Movement → MovementCreated → Stock updated

---

### FASE 4: Migrar Catalog (1 semana)

**Objetivo**: Convertir product/category a Commands/Queries.

##### Tareas:
- [ ] Crear `src/catalog/product/app/commands/` — CreateProduct, UpdateProduct, DeleteProduct
- [ ] Crear `src/catalog/product/app/queries/` — GetProducts, SearchProducts, GetProductById
- [ ] Crear `src/catalog/product/domain/events.py` — ProductCreated, ProductUpdated
- [ ] Crear `src/catalog/product/domain/specifications.py` — ProductInCategory, ProductByName
- [ ] Actualizar Controller
- [ ] Actualizar DI
- [ ] Tests

---

### FASE 5: Simplificar DI Container (1 semana)

**Objetivo**: Reducir `src/__init__.py` de 629 líneas a <100.

##### Tarea 5.1: Implementar DI con decoradores (2 días)

Crear `src/shared/infra/di/decorators.py`:

```python
import inspect
from typing import Type, Callable, Optional
from src.shared.infra.di import DependencyContainer, LifetimeScope
from src.shared.app.repositories import Repository

_container = DependencyContainer()

def _auto_resolve(container, cls, scope_id):
    """Introspect __init__ and resolve dependencies automatically."""
    sig = inspect.signature(cls.__init__)
    params = {}
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        param_type = param.annotation
        if param_type != inspect.Parameter.empty:
            if scope_id:
                params[name] = container.resolve_scoped(param_type, scope_id)
            else:
                params[name] = container.resolve(param_type)
    return cls(**params)

def singleton(cls):
    _container.register(cls, factory=lambda c: cls(), scope=LifetimeScope.SINGLETON)
    return cls

def scoped(cls):
    _container.register(
        cls,
        factory=lambda c, scope_id=None: _auto_resolve(c, cls, scope_id),
        scope=LifetimeScope.SCOPED
    )
    return cls

def repository(entity_type):
    """Decorator: registers class as Repository[entity_type] with SCOPED lifetime."""
    def decorator(cls):
        _container.register(
            Repository[entity_type],
            factory=lambda c, scope_id=None: _auto_resolve(c, cls, scope_id),
            scope=LifetimeScope.SCOPED
        )
        return cls
    return decorator
```

##### Tarea 5.2: Aplicar decoradores a todos los componentes (2 días)

Ejemplo de transformación:

```python
# src/catalog/product/infra/mappers.py
@singleton
class ProductMapper(Mapper[Product, ProductModel]):
    # ...

# src/catalog/product/infra/repositories.py
@repository(Product)
class ProductRepositoryImpl(BaseRepository[Product]):
    __model__ = ProductModel

# src/catalog/product/app/commands/create_product.py
@scoped
class CreateProductCommandHandler:
    def __init__(self, repo: Repository[Product]):
        self.repo = repo
```

##### Tarea 5.3: Reducir src/__init__.py (1 día)

```python
# src/__init__.py (NUEVO — ~50 líneas)
from src.shared.infra.di.decorators import _container as container
from config import config

def initialize():
    container.configure_db(config.DB_CONNECTION_STRING)

    # Auto-discovery: importing modules triggers @singleton/@scoped decorators
    import src.catalog.product.infra.mappers
    import src.catalog.product.infra.repositories
    import src.catalog.product.app.commands
    import src.catalog.product.app.queries
    # ... (un import por módulo)

    # Register event handlers
    import src.inventory.infra.event_handlers
    import src.sales.infra.event_handlers

def get_request_scope_id():
    return str(uuid.uuid4())

# Generic controller dependency factory
def get_controller(controller_type):
    def dependency(scope_id=Depends(get_request_scope_id)):
        controller = container.resolve_scoped(controller_type, scope_id)
        try:
            yield controller
        finally:
            container.close_scope(scope_id)
    return dependency
```

##### Tarea 5.4: Tests de regresión (1 día)

**Checklist Fase 5:**
- [ ] Decoradores implementados y funcionando
- [ ] Todos los módulos usan decoradores
- [ ] `src/__init__.py` < 100 líneas
- [ ] Todos los tests pasan
- [ ] No hay regresiones

---

### FASE 6+: Módulos Nuevos (según necesidad)

Cada módulo nuevo sigue el template:

```
module/
├── domain/
│   ├── entities.py          # Entities con dataclass
│   ├── events.py            # Domain Events
│   ├── specifications.py    # Specifications
│   └── exceptions.py        # Domain exceptions
├── app/
│   ├── commands/             # Command + CommandHandler por operación write
│   └── queries/              # Query + QueryHandler por operación read
└── infra/
    ├── models.py             # SQLAlchemy models
    ├── mappers.py            # @singleton Mapper
    ├── repositories.py       # @repository(Entity) BaseRepository
    ├── controllers.py        # Controller (recibe handlers via DI)
    ├── routes.py             # FastAPI Router
    ├── validators.py         # Pydantic schemas
    └── event_handlers.py     # @event_handler — reacciona a eventos de otros módulos
```

**Orden sugerido** (según valor de negocio):
1. **Sales** (Fase 2 — ya incluido arriba)
2. **Suppliers** — CRUD similar a Customers
3. **Purchases** — Similar a Sales pero inverso (IN en vez de OUT)
4. **Pricing** — Listas de precios, promociones
5. **Warehouse** — Multi-almacén (modifica Stock y Movement)
6. **Reporting** — Solo queries CQRS, sin domain
7. **Accounting** — Event sourcing opcional

---

## Cronograma Visual

```
Semana:  1    2    3    4    5    6    7    8    9    10
         ├────┤
         Fase 0: Fundamentos
              ├─────────┤
              Fase 1: Migrar Customers (piloto)
                        ├──────────────┤
                        Fase 2: Implementar Sales (nuevo)
                                       ├─────────┤
                                       Fase 3: Migrar Inventory
                                                 ├────┤
                                                 Fase 4: Migrar Catalog
                                                      ├────┤
                                                      Fase 5: Simplificar DI
```

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Romper funcionalidad existente | Tests de regresión en cada fase, migración incremental |
| Complejidad innecesaria | Seguir el template, no sobre-diseñar, agregar patrones solo cuando aporten valor |
| Eventos perdidos | Logging en EventBus, retry mechanism futuro |
| DI auto-resolve falla en tipos complejos | Mantener registro manual como fallback, migrar gradualmente |
| Transacciones entre event handlers | UnitOfWork para operaciones multi-repo dentro del mismo handler |

## Notas para futuras sesiones de Claude Code

1. **Si se pide implementar una fase**, leer este documento primero para entender el contexto y el plan.
2. **El código existente en `src/__init__.py`** tiene 629 líneas de registro manual de DI — este es el archivo más grande y más cambiado.
3. **El patrón actual de Use Case** usa TypedDicts (input) y retorna dicts (output). Los nuevos Command Handlers pueden mantener este patrón por compatibilidad.
4. **El DI Container** está en `src/shared/infra/di.py` — entiende SINGLETON, SCOPED y TRANSIENT. Las dependencias SCOPED comparten session de DB dentro del mismo request (scope_id = UUID del request).
5. **BaseRepository** ya tiene `filter()`, `filter_by()` y `first()` — las Specifications se integran via `filter_by_spec()` que llama a `filter()` internamente.
6. **Los event handlers se registran con decoradores** al importar el módulo — por eso el `import src.inventory.infra.event_handlers` en `initialize()`.
7. **main.py** instancia Routers en module level (antes de `initialize()`) — esto funciona porque los Routers no dependen del container directamente, sino que usan `Depends()` de FastAPI.
