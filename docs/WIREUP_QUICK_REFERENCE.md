# Wireup - Referencia Rápida

Snippets de código para copy-paste durante la migración.

---

## 🔧 1. Mapper

```python
from wireup import injectable

@injectable  # ← Agregar esta línea
class {Entity}Mapper(Mapper[{Entity}, {Entity}Model]):
    # ... código sin cambios
```

**Archivo:** `src/{module}/infra/mappers.py`

---

## 🔧 2. Repository

```python
from sqlalchemy.orm import Session
from wireup import injectable
from src.shared.app.repositories import Repository
from src.{module}.infra.mappers import {Entity}Mapper

@injectable(lifetime="scoped")  # ← Agregar
class {Entity}RepositoryImpl(BaseRepository[{Entity}]):
    __model__ = {Entity}Model


@injectable(lifetime="scoped", as_type=Repository[{Entity}])  # ← Agregar
def create_{entity}_repository(
    session: Session,
    mapper: {Entity}Mapper
) -> Repository[{Entity}]:
    return {Entity}RepositoryImpl(session, mapper)
```

**Archivo:** `src/{module}/infra/repositories.py`

---

## 🔧 3. Command Handler

```python
from wireup import injectable

@injectable(lifetime="scoped")  # ← Agregar esta línea
class Create{Entity}CommandHandler(CommandHandler[Create{Entity}Command, dict]):
    def __init__(self, repo: Repository[{Entity}]):
        self.repo = repo
    # ... código sin cambios
```

**Archivo:** `src/{module}/app/commands/{action}_{entity}.py`

---

## 🔧 4. Query Handler

```python
from wireup import injectable

@injectable(lifetime="scoped")  # ← Agregar esta línea
class GetAll{Entities}QueryHandler(QueryHandler[GetAll{Entities}Query, list[dict]]):
    def __init__(self, repo: Repository[{Entity}]):
        self.repo = repo
    # ... código sin cambios
```

**Archivo:** `src/{module}/app/queries/get_{entities}.py`

---

## 🔧 5. Controller

```python
from wireup import injectable

@injectable(lifetime="scoped")  # ← Agregar esta línea
class {Entity}Controller:
    def __init__(
        self,
        create_handler: Create{Entity}CommandHandler,
        # ... otros handlers
    ):
        # ... código sin cambios
```

**Archivo:** `src/{module}/infra/controllers.py`

---

## 🔧 6. Router

### Imports (agregar)
```python
from wireup import Injected
```

### Remover imports
```python
# ELIMINAR estas líneas:
from src import get_{entity}_controller
from fastapi import Depends  # Si no se usa en otro lado
```

### Métodos de ruta (actualizar TODOS)

**ANTES:**
```python
def create(
    self,
    new_{entity}: {Entity}Input,
    controller: {Entity}Controller = Depends(get_{entity}_controller),
):
    return controller.create(new_{entity})
```

**DESPUÉS:**
```python
def create(
    self,
    new_{entity}: {Entity}Input,
    controller: Injected[{Entity}Controller],  # ← Cambio
):
    return controller.create(new_{entity})
```

**Archivo:** `src/{module}/infra/routes.py`

---

## 🔧 7. Wireup Container

### Imports (agregar en `src/__init__.py`)

```python
# En create_wireup_container(), después de imports existentes:
from src.{module}.infra.mappers import {Entity}Mapper
from src.{module}.infra.repositories import create_{entity}_repository
from src.{module}.app.commands.create_{entity} import Create{Entity}CommandHandler
from src.{module}.app.commands.update_{entity} import Update{Entity}CommandHandler
from src.{module}.app.commands.delete_{entity} import Delete{Entity}CommandHandler
from src.{module}.app.queries.get_{entities} import (
    GetAll{Entities}QueryHandler,
    Get{Entity}ByIdQueryHandler,
)
from src.{module}.infra.controllers import {Entity}Controller
```

### Registration (agregar en lista `injectables=[]`)

```python
container = create_sync_container(
    injectables=[
        get_db_session,

        # ... componentes existentes

        # {Entity} module
        {Entity}Mapper,
        create_{entity}_repository,
        Create{Entity}CommandHandler,
        Update{Entity}CommandHandler,
        Delete{Entity}CommandHandler,
        GetAll{Entities}QueryHandler,
        Get{Entity}ByIdQueryHandler,
        {Entity}Controller,
    ]
)
```

**Archivo:** `src/__init__.py` - función `create_wireup_container()`

---

## 🔧 8. Remover de Custom DI

### Mapper

```python
def init_mappers() -> None:
    # ELIMINAR o comentar:
    # container.register(
    #     {Entity}Mapper,
    #     factory=lambda c: {Entity}Mapper(),
    #     scope=LifetimeScope.SINGLETON,
    # )
```

### Repository

```python
def init_repositories() -> None:
    # ELIMINAR o comentar:
    # container.register(
    #     Repository[{Entity}],
    #     factory=lambda c, scope_id=None: {Entity}RepositoryImpl(...),
    #     scope=LifetimeScope.SCOPED,
    # )
```

### Handlers

```python
def init_handlers() -> None:
    # ELIMINAR o comentar TODOS los handlers del módulo:
    # container.register(Create{Entity}CommandHandler, ...)
    # container.register(Update{Entity}CommandHandler, ...)
    # container.register(Delete{Entity}CommandHandler, ...)
    # container.register(GetAll{Entities}QueryHandler, ...)
    # container.register(Get{Entity}ByIdQueryHandler, ...)
```

### Controller

```python
def init_controllers() -> None:
    # ELIMINAR o comentar:
    # container.register(
    #     {Entity}Controller,
    #     factory=lambda c, scope_id=None: {Entity}Controller(...),
    #     scope=LifetimeScope.SCOPED,
    # )
```

### Dependency Provider Function

```python
# ELIMINAR completamente esta función:
def get_{entity}_controller(
    scope_id: str = Depends(get_request_scope_id),
) -> {Entity}Controller:
    ...
```

**Archivo:** `src/__init__.py`

---

## 🧪 Verificación

### Después de cada módulo

```bash
# 1. Verificar que app inicia
.venv/bin/python -c "
import sys
sys.path.insert(0, '.')
from main import app, wireup_container
print('✓ App OK')
"

# 2. Ejecutar tests del módulo
.venv/bin/python -m pytest tests/unit/{module}/ -v

# 3. Commit
git add .
git commit -m "feat: migrate {module} module to wireup DI"
```

---

## 📝 Casos Especiales

### Módulo con Múltiples Entidades (ej: Sales)

Si un módulo tiene múltiples entidades (Sale, SaleItem, Payment):

1. **Decorar cada mapper:**
   ```python
   @injectable
   class SaleMapper(...): ...

   @injectable
   class SaleItemMapper(...): ...

   @injectable
   class PaymentMapper(...): ...
   ```

2. **Crear factory para cada repositorio:**
   ```python
   @injectable(lifetime="scoped", as_type=Repository[Sale])
   def create_sale_repository(...): ...

   @injectable(lifetime="scoped", as_type=Repository[SaleItem])
   def create_sale_item_repository(...): ...

   @injectable(lifetime="scoped", as_type=Repository[Payment])
   def create_payment_repository(...): ...
   ```

3. **Handlers que usan múltiples repositorios:**
   ```python
   @injectable(lifetime="scoped")
   class AddSaleItemCommandHandler:
       def __init__(
           self,
           sale_repo: Repository[Sale],
           item_repo: Repository[SaleItem],
       ):
           self.sale_repo = sale_repo
           self.item_repo = item_repo
   ```

   Wireup inyectará ambos automáticamente.

---

### Handler sin Repositorio (edge case)

Si un handler NO usa repositorio (raro), solo decorar:

```python
@injectable(lifetime="scoped")
class SomeSpecialHandler:
    def __init__(self):
        # Sin dependencias
        pass
```

---

## 🚨 Errores Comunes

### ❌ Error: "as_type parameter is missing"

**Problema:**
```python
@injectable(lifetime="scoped")  # ← Falta as_type
def create_product_repository(...) -> Repository[Product]:
    ...
```

**Solución:**
```python
@injectable(lifetime="scoped", as_type=Repository[Product])  # ✅
def create_product_repository(...) -> Repository[Product]:
    ...
```

---

### ❌ Error: "Forgot to register injectable"

**Problema:** Decoraste un handler pero no lo agregaste al container.

**Solución:** Verifica que TODOS los componentes decorados estén en la lista `injectables=[]` de `create_wireup_container()`.

---

### ❌ Error: Olvidaste actualizar un método del router

**Problema:** Solo actualizaste algunos métodos con `Injected[]`, otros siguen con `Depends()`.

**Solución:** Busca `Depends(get_{entity}_controller)` en el archivo y reemplaza TODAS las ocurrencias.

**Regex para buscar:**
```
Depends\(get_\w+_controller\)
```

---

## 🎯 Template Completo para un Módulo

### Checklist de 5 minutos

```markdown
- [ ] Agregar `from wireup import injectable` a mappers.py
- [ ] Agregar `@injectable` antes de class {Entity}Mapper
- [ ] Agregar imports a repositories.py (Session, injectable, Repository, mapper)
- [ ] Agregar `@injectable(lifetime="scoped")` a {Entity}RepositoryImpl
- [ ] Crear factory function create_{entity}_repository con as_type
- [ ] Buscar todos los archivos .py en app/commands/*.py
- [ ] Agregar `from wireup import injectable` a cada uno
- [ ] Agregar `@injectable(lifetime="scoped")` a cada handler
- [ ] Repetir para app/queries/*.py
- [ ] Agregar `from wireup import injectable` a controllers.py
- [ ] Agregar `@injectable(lifetime="scoped")` a {Entity}Controller
- [ ] En routes.py: agregar `from wireup import Injected`
- [ ] En routes.py: remover import get_{entity}_controller
- [ ] En routes.py: buscar/reemplazar `Depends(get_{entity}_controller)` → `Injected[{Entity}Controller]`
- [ ] En src/__init__.py: agregar imports en create_wireup_container()
- [ ] En src/__init__.py: agregar componentes a injectables=[]
- [ ] En src/__init__.py: comentar/eliminar en init_mappers()
- [ ] En src/__init__.py: comentar/eliminar en init_repositories()
- [ ] En src/__init__.py: comentar/eliminar TODOS los handlers en init_handlers()
- [ ] En src/__init__.py: comentar/eliminar en init_controllers()
- [ ] En src/__init__.py: eliminar función get_{entity}_controller()
- [ ] Verificar: python -c "from main import app; print('OK')"
- [ ] Ejecutar tests: pytest tests/unit/{module}/ -v
- [ ] Commit: git commit -m "feat: migrate {module} to wireup"
```

---

## 📚 Más Información

Ver documentación completa en [WIREUP_MIGRATION_GUIDE.md](./WIREUP_MIGRATION_GUIDE.md)
