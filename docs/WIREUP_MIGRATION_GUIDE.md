# Guía de Migración: Custom DI → Wireup 2.7.0

## 📋 Índice

1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Estado Actual](#estado-actual)
3. [Patrón de Migración](#patrón-de-migración)
4. [Checklist por Módulo](#checklist-por-módulo)
5. [Ejemplos de Código](#ejemplos-de-código)
6. [Verificación y Testing](#verificación-y-testing)
7. [Troubleshooting](#troubleshooting)
8. [Próximos Pasos](#próximos-pasos)

---

## 🎯 Resumen del Proyecto

### Objetivo

Migrar de un contenedor de DI personalizado (~700 líneas de boilerplate) a **wireup 2.7.0**, una librería moderna de inyección de dependencias que aprovecha type hints de Python.

### Beneficios Esperados

- ✅ **Reducción de código**: ~700 líneas de boilerplate eliminadas
- ✅ **Type safety**: Validación en tiempo de compilación
- ✅ **Fail-fast**: Errores de dependencias detectados al inicio, no en runtime
- ✅ **Mantenibilidad**: Decoradores más claros que factories anidados
- ✅ **Menos funciones**: Eliminar 7 funciones `get_*_controller()`

### Estrategia de Migración

**Incremental con coexistencia**: Ambos sistemas de DI coexisten durante la migración. Se migra módulo por módulo, permitiendo rollback aislado si hay problemas.

---

## 📊 Estado Actual

### ✅ Completado

#### Phase 0: Infraestructura (Completado)
- [x] Actualizar a wireup 2.7.0
- [x] Crear `src/shared/infra/db_session.py` con factory de sesión
- [x] Crear función `create_wireup_container()` en `src/__init__.py`
- [x] Integrar wireup con FastAPI en `main.py`
- [x] Verificar coexistencia con custom DI

#### Phase 1: Módulo Piloto - Category (Completado)
- [x] Decorar `CategoryMapper` con `@injectable`
- [x] Decorar `CategoryRepositoryImpl` + crear factory
- [x] Decorar 5 handlers de Category
- [x] Decorar `CategoryController`
- [x] Actualizar `CategoryRouter` con patrón `Injected[]`
- [x] Registrar en `create_wireup_container()`
- [x] Remover de custom DI
- [x] Eliminar función `get_category_controller()`
- [x] Verificar tests (12/12 passed ✅)

**Reducción de código en Phase 1:** ~50 líneas de boilerplate eliminadas

### 🔄 Pendiente

#### Phase 2: Módulos Restantes
- [ ] **Product** (5 handlers, 1 controller)
- [ ] **Customer** (10 handlers, 1 controller)
- [ ] **CustomerContact** (5 handlers, 1 controller)
- [ ] **Movement** (3 handlers, 1 controller)
- [ ] **Stock** (3 handlers, 1 controller)
- [ ] **Sale** (11 handlers, 1 controller)

#### Phase 3: Cleanup
- [ ] Eliminar `init_mappers()`, `init_repositories()`, `init_handlers()`, `init_controllers()`
- [ ] Eliminar funciones `get_*_controller()` restantes
- [ ] Eliminar `src/shared/infra/di.py`
- [ ] Eliminar imports de `DependencyContainer`, `LifetimeScope`
- [ ] Verificación final: tests completos + performance

---

## 🔧 Patrón de Migración

### Estructura de Archivos por Módulo

Usando `product` como ejemplo:

```
src/catalog/product/
├── app/
│   ├── commands/
│   │   ├── create_product.py     → Decorar handler
│   │   ├── update_product.py     → Decorar handler
│   │   └── delete_product.py     → Decorar handler
│   └── queries/
│       └── get_products.py       → Decorar handlers
├── infra/
│   ├── mappers.py                → Decorar mapper
│   ├── repositories.py           → Decorar + crear factory
│   ├── controllers.py            → Decorar controller
│   └── routes.py                 → Actualizar con Injected[]
```

### Paso a Paso por Módulo

#### 1. Decorar el Mapper

**Archivo:** `src/{module}/infra/mappers.py`

```python
from wireup import injectable

@injectable  # Singleton por defecto (mappers son stateless)
class ProductMapper(Mapper[Product, ProductModel]):
    # ... código existente sin cambios
```

**¿Por qué singleton?** Los mappers no tienen estado, pueden compartirse.

---

#### 2. Decorar el Repository + Crear Factory

**Archivo:** `src/{module}/infra/repositories.py`

```python
from sqlalchemy.orm import Session
from wireup import injectable

from src.shared.app.repositories import Repository
from src.{module}.domain.entities import Product
from src.{module}.infra.mappers import ProductMapper

# Decorar la implementación
@injectable(lifetime="scoped")
class ProductRepositoryImpl(BaseRepository[Product]):
    __model__ = ProductModel

# Factory para binding de tipo genérico
@injectable(lifetime="scoped", as_type=Repository[Product])
def create_product_repository(
    session: Session,
    mapper: ProductMapper
) -> Repository[Product]:
    """Factory para inyectar Repository[Product].

    Args:
        session: Sesión de BD (inyectada por wireup, scoped)
        mapper: ProductMapper (inyectado por wireup, singleton)

    Returns:
        Repository[Product]: Implementación concreta
    """
    return ProductRepositoryImpl(session, mapper)
```

**¿Por qué la factory?** Los handlers piden `Repository[Product]` (genérico), no `ProductRepositoryImpl` (concreto). El parámetro `as_type` le dice a wireup: "cuando pidan `Repository[Product]`, usa esta factory".

**¿Por qué scoped?** Necesita una sesión de BD que es scoped (una por request).

---

#### 3. Decorar los Command Handlers

**Archivo:** `src/{module}/app/commands/create_{entity}.py`

```python
from wireup import injectable

@injectable(lifetime="scoped")
class CreateProductCommandHandler(CommandHandler[CreateProductCommand, dict]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, command: CreateProductCommand) -> dict:
        # ... código existente sin cambios
```

**Repetir para:** update, delete, y cualquier otro command handler.

**¿Por qué scoped?** Depende del repositorio que es scoped.

---

#### 4. Decorar los Query Handlers

**Archivo:** `src/{module}/app/queries/get_{entities}.py`

```python
from wireup import injectable

@injectable(lifetime="scoped")
class GetAllProductsQueryHandler(QueryHandler[GetAllProductsQuery, list[dict]]):
    def __init__(self, repo: Repository[Product]):
        self.repo = repo

    def handle(self, query: GetAllProductsQuery) -> list[dict]:
        # ... código existente sin cambios
```

**Repetir para:** cada query handler en el archivo.

---

#### 5. Decorar el Controller

**Archivo:** `src/{module}/infra/controllers.py`

```python
from wireup import injectable

@injectable(lifetime="scoped")
class ProductController:
    def __init__(
        self,
        create_handler: CreateProductCommandHandler,
        update_handler: UpdateProductCommandHandler,
        # ... todos los handlers
    ):
        # ... código existente sin cambios
```

**¿Por qué scoped?** Depende de handlers que son scoped.

---

#### 6. Actualizar el Router con `Injected[]`

**Archivo:** `src/{module}/infra/routes.py`

**ANTES (custom DI):**
```python
from fastapi import APIRouter, Depends
from src import get_product_controller

class ProductRouter:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def create(
        self,
        new_product: ProductInput,
        controller: ProductController = Depends(get_product_controller),
    ):
        return controller.create(new_product)
```

**DESPUÉS (wireup):**
```python
from fastapi import APIRouter
from wireup import Injected

class ProductRouter:
    def __init__(self):
        """Router usando wireup Injected[] para scoped controller."""
        self.router = APIRouter()
        self._setup_routes()

    def create(
        self,
        new_product: ProductInput,
        controller: Injected[ProductController],  # ← Cambio principal
    ):
        return controller.create(new_product)
```

**Cambios necesarios:**
1. Importar `Injected` de `wireup`
2. Remover import de `get_product_controller`
3. Remover import de `Depends` (si no se usa en otro lado)
4. En **CADA método de ruta**: cambiar `Depends(get_product_controller)` por `Injected[ProductController]`

**¿Por qué `Injected[]`?** El controller es scoped (necesita una sesión de BD por request). `Injected[]` le dice a wireup: "resuelve esto en cada request".

---

#### 7. Registrar en Wireup Container

**Archivo:** `src/__init__.py`

```python
def create_wireup_container():
    from wireup import create_sync_container
    from src.shared.infra.db_session import configure_session_factory, get_db_session

    # Importar componentes del módulo Product
    from src.catalog.product.infra.mappers import ProductMapper
    from src.catalog.product.infra.repositories import create_product_repository
    from src.catalog.product.app.commands.create_product import CreateProductCommandHandler
    from src.catalog.product.app.commands.update_product import UpdateProductCommandHandler
    from src.catalog.product.app.commands.delete_product import DeleteProductCommandHandler
    from src.catalog.product.app.queries.get_products import (
        GetAllProductsQueryHandler,
        GetProductByIdQueryHandler,
    )
    from src.catalog.product.infra.controllers import ProductController

    # ... imports de otros módulos ya migrados (Category, etc.)

    configure_session_factory(config.DB_CONNECTION_STRING)

    container = create_sync_container(
        injectables=[
            get_db_session,

            # Category (ya migrado)
            CategoryMapper,
            create_category_repository,
            # ... handlers de Category

            # Product (nuevo)
            ProductMapper,
            create_product_repository,
            CreateProductCommandHandler,
            UpdateProductCommandHandler,
            DeleteProductCommandHandler,
            GetAllProductsQueryHandler,
            GetProductByIdQueryHandler,
            ProductController,
        ]
    )

    return container
```

**Importante:** Wireup valida el grafo de dependencias al crear el container. Si falta algo, fallará inmediatamente (fail-fast).

---

#### 8. Remover del Custom DI

**Archivo:** `src/__init__.py`

```python
def init_mappers() -> None:
    """Initializes all mappers (legacy custom DI)."""
    # Product mapper removed - now registered in wireup
    # container.register(ProductMapper, ...) ← ELIMINAR
```

```python
def init_repositories() -> None:
    """Initializes all repositories (legacy custom DI)."""
    # Product repository removed - now registered in wireup
    # container.register(Repository[Product], ...) ← ELIMINAR
```

```python
def init_handlers() -> None:
    """Initializes all command/query handlers (legacy custom DI)."""
    # Product handlers removed - now registered in wireup
    # container.register(CreateProductCommandHandler, ...) ← ELIMINAR todas
```

```python
def init_controllers() -> None:
    """Initializes all controllers (legacy custom DI)."""
    # ProductController removed - now registered in wireup
    # container.register(ProductController, ...) ← ELIMINAR
```

**Eliminar función de dependency provider:**
```python
# Eliminar completamente
def get_product_controller(...):  # ← ELIMINAR TODA LA FUNCIÓN
    ...
```

---

#### 9. Actualizar `main.py` (Solo si es necesario)

Si instancias el router desde el container (no aplica para patrón `Injected[]`):

```python
# Router ya usa Injected[], instanciar normalmente
product_router = ProductRouter()  # Sin cambios
```

---

## ✅ Checklist por Módulo

Copia este checklist para cada módulo:

```markdown
### Módulo: [NOMBRE]

- [ ] 1. Decorar mapper con `@injectable`
- [ ] 2. Decorar repository con `@injectable(lifetime="scoped")`
- [ ] 3. Crear factory function `create_{entity}_repository` con `as_type`
- [ ] 4. Decorar TODOS los command handlers con `@injectable(lifetime="scoped")`
- [ ] 5. Decorar TODOS los query handlers con `@injectable(lifetime="scoped")`
- [ ] 6. Decorar controller con `@injectable(lifetime="scoped")`
- [ ] 7. Actualizar router: importar `Injected`, cambiar TODOS los métodos
- [ ] 8. Agregar imports al `create_wireup_container()` en `src/__init__.py`
- [ ] 9. Agregar componentes a lista `injectables=[]` en container
- [ ] 10. Remover mapper de `init_mappers()`
- [ ] 11. Remover repository de `init_repositories()`
- [ ] 12. Remover TODOS los handlers de `init_handlers()`
- [ ] 13. Remover controller de `init_controllers()`
- [ ] 14. Eliminar función `get_{entity}_controller()`
- [ ] 15. Verificar que app inicia sin errores
- [ ] 16. Ejecutar tests del módulo: `pytest tests/unit/{module}/ -v`
- [ ] 17. Commit: `git commit -m "feat: migrate {module} to wireup"`
```

---

## 📝 Ejemplos de Código

### Módulo de Referencia: Category (Completado)

Todos los archivos del módulo Category están completamente migrados y pueden usarse como referencia:

**Mappers:**
- `src/catalog/product/infra/mappers.py` (línea 10)

**Repositories:**
- `src/catalog/product/infra/repositories.py` (líneas 11-34)

**Command Handlers:**
- `src/catalog/product/app/commands/create_category.py` (línea 18)
- `src/catalog/product/app/commands/update_category.py` (línea 19)
- `src/catalog/product/app/commands/delete_category.py` (línea 17)

**Query Handlers:**
- `src/catalog/product/app/queries/get_categories.py` (líneas 16, 31)

**Controller:**
- `src/catalog/product/infra/controllers.py` (línea 36)

**Router:**
- `src/catalog/product/infra/routes.py` (líneas 2, 15-62)

**Container Registration:**
- `src/__init__.py` (líneas 798-856)

---

## 🧪 Verificación y Testing

### Verificación Rápida Después de Cada Módulo

```bash
# 1. Verificar que la app inicia sin errores
.venv/bin/python -c "
import sys
sys.path.insert(0, '.')
from main import app, wireup_container
print('✓ App initialized successfully')
print(f'✓ Total routes: {len(app.routes)}')
"

# 2. Ejecutar tests del módulo
.venv/bin/python -m pytest tests/unit/{module}/ -v

# 3. Verificar conteo de handlers registrados (opcional)
.venv/bin/python -c "
import sys
sys.path.insert(0, '.')
from src import create_wireup_container
container = create_wireup_container()
print(f'✓ Wireup container created with all dependencies')
"
```

### Tests Completos (Al final de Phase 2)

```bash
# Ejecutar todos los tests
.venv/bin/python -m pytest tests/ -v

# Verificar cobertura
.venv/bin/python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 🐛 Troubleshooting

### Error: "Singletons can only depend on other singletons"

**Causa:** Intentaste decorar un router con `@injectable` (singleton) e inyectar el controller (scoped) en el constructor.

**Solución:** NO decorar el router, usar patrón `Injected[]` en los métodos:

```python
# ❌ INCORRECTO
@injectable
class ProductRouter:
    def __init__(self, controller: ProductController):  # Error!
        ...

# ✅ CORRECTO
class ProductRouter:  # Sin decorator
    def __init__(self):
        ...

    def create(self, data: Input, controller: Injected[ProductController]):
        ...
```

---

### Error: "Injectable not found" o "Missing dependency"

**Causa:** Olvidaste registrar un componente en `create_wireup_container()`.

**Solución:** Verifica que TODOS los componentes decorados estén en la lista `injectables=[]`:

```python
container = create_sync_container(
    injectables=[
        get_db_session,
        ProductMapper,  # ← ¿Está?
        create_product_repository,  # ← ¿Está?
        CreateProductCommandHandler,  # ← ¿Está?
        # ... TODOS los handlers
        ProductController,  # ← ¿Está?
    ]
)
```

---

### Error: "Database not configured"

**Causa:** La función `configure_session_factory()` no se llamó antes de crear el container.

**Solución:** Verifica el orden en `create_wireup_container()`:

```python
def create_wireup_container():
    # 1. Primero configurar DB
    configure_session_factory(config.DB_CONNECTION_STRING)

    # 2. Luego crear container
    container = create_sync_container(injectables=[...])
```

---

### Tests fallan después de la migración

**Diagnóstico:**

1. ¿Los tests crean el wireup container?
2. ¿Los tests mockean correctamente las dependencias?
3. ¿El test DB está configurado?

**Solución:** Los tests unitarios NO deberían depender del container. Usan mocks:

```python
# Test unitario - inyección manual, sin container
def test_create_product():
    mock_repo = Mock()
    handler = CreateProductCommandHandler(repo=mock_repo)
    # ... test logic
```

---

### Error: Generic type `Repository[Entity]` no resuelve

**Causa:** Olvidaste crear la factory function o falta el parámetro `as_type`.

**Solución:** Verifica el patrón completo:

```python
@injectable(lifetime="scoped", as_type=Repository[Product])  # ← as_type!
def create_product_repository(
    session: Session,
    mapper: ProductMapper
) -> Repository[Product]:  # ← Return type explícito
    return ProductRepositoryImpl(session, mapper)
```

---

## 🚀 Próximos Pasos

### Orden Sugerido de Migración (Phase 2)

1. **Product** (mismo módulo que Category, fácil)
2. **Movement** (3 handlers, módulo pequeño)
3. **Stock** (3 handlers, módulo pequeño)
4. **CustomerContact** (5 handlers, depende de Customer)
5. **Customer** (10 handlers, módulo más grande)
6. **Sale** (11 handlers, el más complejo)

**Razón del orden:** Empezar con módulos pequeños/familiares para ganar confianza, dejar los complejos al final.

### Comandos para Cada Sesión

```bash
# 1. Crear rama para el módulo
git checkout -b feat/wireup-migration-{module}

# 2. Migrar siguiendo el checklist (ver arriba)

# 3. Verificar
.venv/bin/python -m pytest tests/unit/{module}/ -v

# 4. Commit
git add .
git commit -m "feat: migrate {module} module to wireup DI"

# 5. Merge a main (o PR)
git checkout master
git merge feat/wireup-migration-{module}
```

### Phase 3: Cleanup Final

**Solo después de migrar TODOS los módulos:**

```bash
# Eliminar archivos obsoletos
rm src/shared/infra/di.py

# Eliminar funciones en src/__init__.py:
# - init_mappers()
# - init_repositories()
# - init_handlers()
# - init_controllers()
# - initialize()
# - get_request_scope_id()
# - Todos los get_*_controller()

# Limpiar imports
# - DependencyContainer
# - LifetimeScope
# - container global variable

# Commit final
git commit -m "feat: complete wireup migration - remove custom DI"
```

### Métricas de Éxito

Al terminar Phase 3:

- ✅ **~700 líneas de código eliminadas** (custom DI boilerplate)
- ✅ **7 funciones `get_*_controller()` eliminadas**
- ✅ **Todos los tests pasan**
- ✅ **Startup validation** (errores detectados al inicio, no en runtime)
- ✅ **Type safety** (type hints validados por wireup)

---

## 📚 Referencias

- **Wireup Documentation:** https://maldoinc.github.io/wireup/latest/
- **FastAPI Integration:** https://maldoinc.github.io/wireup/latest/integrations/fastapi/
- **Generic Types:** https://maldoinc.github.io/wireup/latest/usage/parameters/#generic-types

---

## 📌 Notas Importantes

1. **No elimines el custom DI hasta Phase 3**: Ambos sistemas deben coexistir hasta migrar todos los módulos.

2. **Commit frecuente**: Haz commit después de cada módulo para facilitar rollback.

3. **Tests primero**: Si los tests del módulo fallan, no continues a registrar en wireup.

4. **Verifica startup**: Cada vez que agregues componentes a wireup, verifica que `create_wireup_container()` no falle.

5. **Patrón `Injected[]` es para scoped dependencies**: Si alguna vez tienes un singleton que necesita inyección, puede ir en el constructor sin problemas.

6. **Factory functions son necesarias para genéricos**: `Repository[T]` siempre necesita factory con `as_type`.

---

**Última actualización:** 2026-02-11
**Módulos migrados:** 1/7 (Category ✅)
**Progreso Phase 2:** 14% completado
