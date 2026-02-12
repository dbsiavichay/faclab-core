# Estado de Migración: Wireup 2.7.0

**Última actualización:** 2026-02-11
**Progreso general:** 14% (1/7 módulos)

---

## 📊 Resumen Ejecutivo

| Fase | Estado | Progreso | Archivos | LoC Eliminadas |
|------|--------|----------|----------|----------------|
| Phase 0: Infraestructura | ✅ Completado | 100% | 4 | 0 |
| Phase 1: Módulo Piloto (Category) | ✅ Completado | 100% | 10 | ~50 |
| Phase 2: Módulos Restantes | 🔄 Pendiente | 0% | ~60 | ~650 |
| Phase 3: Cleanup Final | ⏳ Bloqueado | 0% | 3 | ~200 |
| **TOTAL** | 🔄 En Progreso | **14%** | **77** | **~900** |

---

## ✅ Phase 0: Infraestructura (Completado)

**Fecha:** 2026-02-11

### Archivos Creados
- ✅ `src/shared/infra/db_session.py` - Factory de sesión con generadores

### Archivos Modificados
- ✅ `requirements.txt` - Actualizado a wireup==2.7.0
- ✅ `src/__init__.py` - Agregada función `create_wireup_container()`
- ✅ `main.py` - Integración de wireup con FastAPI

### Verificación
```bash
✅ App inicia correctamente
✅ Ambos DI coexisten sin conflictos
✅ 41 rutas registradas
```

---

## ✅ Phase 1: Módulo Category (Completado)

**Fecha:** 2026-02-11
**Handlers migrados:** 5
**Tests:** 12/12 ✅

### Archivos Modificados

#### Domain (0 cambios)
- Sin cambios en entities/events

#### Application Layer
- ✅ `src/catalog/product/app/commands/create_category.py`
  - Handler decorado con `@injectable(lifetime="scoped")`
- ✅ `src/catalog/product/app/commands/update_category.py`
  - Handler decorado con `@injectable(lifetime="scoped")`
- ✅ `src/catalog/product/app/commands/delete_category.py`
  - Handler decorado con `@injectable(lifetime="scoped")`
- ✅ `src/catalog/product/app/queries/get_categories.py`
  - 2 handlers decorados con `@injectable(lifetime="scoped")`

#### Infrastructure Layer
- ✅ `src/catalog/product/infra/mappers.py`
  - CategoryMapper decorado con `@injectable`
- ✅ `src/catalog/product/infra/repositories.py`
  - CategoryRepositoryImpl decorado
  - Factory `create_category_repository()` creada
- ✅ `src/catalog/product/infra/controllers.py`
  - CategoryController decorado con `@injectable(lifetime="scoped")`
- ✅ `src/catalog/product/infra/routes.py`
  - Actualizado con patrón `Injected[CategoryController]`

#### DI Registration
- ✅ `src/__init__.py`
  - Agregados imports y registros en `create_wireup_container()`
  - Removido CategoryMapper de `init_mappers()`
  - Removido Repository[Category] de `init_repositories()`
  - Removidos 5 handlers de `init_handlers()`
  - Removido CategoryController de `init_controllers()`
  - Eliminada función `get_category_controller()`

### Verificación
```bash
✅ pytest tests/unit/catalog/ -k category -v
   → 12 passed, 18 deselected
✅ App inicia sin errores
✅ Container resuelve todas las dependencias
```

### LoC Eliminadas
- ~50 líneas de boilerplate (registros custom DI + get_category_controller)

---

## 🔄 Phase 2: Módulos Restantes (Pendiente)

### 1. Product Module
**Estado:** ⏳ Pendiente
**Prioridad:** Alta (mismo módulo que Category)
**Handlers:** 5
**Tests:** ~10

**Archivos a modificar:**
- [ ] `src/catalog/product/infra/mappers.py` (ProductMapper)
- [ ] `src/catalog/product/infra/repositories.py` (ProductRepositoryImpl + factory)
- [ ] `src/catalog/product/app/commands/create_product.py`
- [ ] `src/catalog/product/app/commands/update_product.py`
- [ ] `src/catalog/product/app/commands/delete_product.py`
- [ ] `src/catalog/product/app/queries/get_products.py`
- [ ] `src/catalog/product/infra/controllers.py` (ProductController)
- [ ] `src/catalog/product/infra/routes.py` (ProductRouter con Injected[])
- [ ] `src/__init__.py` (registrar + remover custom DI)

**Estimación:** 30 minutos

---

### 2. Movement Module
**Estado:** ⏳ Pendiente
**Prioridad:** Media
**Handlers:** 3 (1 command, 2 queries)
**Tests:** ~5

**Archivos a modificar:**
- [ ] `src/inventory/movement/infra/mappers.py`
- [ ] `src/inventory/movement/infra/repositories.py`
- [ ] `src/inventory/movement/app/commands/create_movement.py`
- [ ] `src/inventory/movement/app/queries/{get_all, get_by_id}.py`
- [ ] `src/inventory/movement/infra/controllers.py`
- [ ] `src/inventory/movement/infra/routes.py`
- [ ] `src/__init__.py`

**Estimación:** 20 minutos

---

### 3. Stock Module
**Estado:** ⏳ Pendiente
**Prioridad:** Media
**Handlers:** 3 (solo queries)
**Tests:** ~5

**Archivos a modificar:**
- [ ] `src/inventory/stock/infra/mappers.py`
- [ ] `src/inventory/stock/infra/repositories.py`
- [ ] `src/inventory/stock/app/queries/{get_all, get_by_id, get_by_product}.py`
- [ ] `src/inventory/stock/infra/controllers.py`
- [ ] `src/inventory/stock/infra/routes.py`
- [ ] `src/__init__.py`

**Estimación:** 20 minutos

---

### 4. CustomerContact Module
**Estado:** ⏳ Pendiente
**Prioridad:** Baja (depende de Customer)
**Handlers:** 5 (3 commands, 2 queries)
**Tests:** ~8

**Archivos a modificar:**
- [ ] `src/customers/infra/mappers.py` (CustomerContactMapper)
- [ ] `src/customers/infra/repositories.py` (CustomerContactRepositoryImpl + factory)
- [ ] `src/customers/app/commands/{create, update, delete}_customer_contact.py`
- [ ] `src/customers/app/queries/{get_by_id, get_by_customer_id}.py`
- [ ] `src/customers/infra/controllers.py` (CustomerContactController)
- [ ] `src/customers/infra/routes.py` (CustomerContactRouter)
- [ ] `src/__init__.py`

**Estimación:** 25 minutos

---

### 5. Customer Module
**Estado:** ⏳ Pendiente
**Prioridad:** Media
**Handlers:** 10 (5 commands, 3 queries)
**Tests:** ~15

**Archivos a modificar:**
- [ ] `src/customers/infra/mappers.py` (CustomerMapper)
- [ ] `src/customers/infra/repositories.py` (CustomerRepositoryImpl + factory)
- [ ] `src/customers/app/commands/{create, update, delete, activate, deactivate}_customer.py`
- [ ] `src/customers/app/queries/{get_all, get_by_id, get_by_tax_id}.py`
- [ ] `src/customers/infra/controllers.py` (CustomerController)
- [ ] `src/customers/infra/routes.py` (CustomerRouter)
- [ ] `src/__init__.py`

**Estimación:** 40 minutos

---

### 6. Sale Module
**Estado:** ⏳ Pendiente
**Prioridad:** Baja (más complejo)
**Handlers:** 11 (6 commands, 4 queries)
**Entities:** 3 (Sale, SaleItem, Payment)
**Tests:** ~20

**Archivos a modificar:**
- [ ] `src/sales/infra/mappers.py` (SaleMapper, SaleItemMapper, PaymentMapper)
- [ ] `src/sales/infra/repositories.py` (3 repositorios + 3 factories)
- [ ] `src/sales/app/commands/{create, add_item, remove_item, confirm, cancel, register_payment}.py`
- [ ] `src/sales/app/queries/{get_all, get_by_id, get_items, get_payments}.py`
- [ ] `src/sales/infra/controllers.py` (SaleController)
- [ ] `src/sales/infra/routes.py` (SaleRouter)
- [ ] `src/__init__.py`

**Estimación:** 60 minutos

**Nota:** Sale es el módulo más complejo (3 entidades, handlers con múltiples repos).

---

## ⏳ Phase 3: Cleanup Final (Bloqueado)

**Prerequisito:** Completar todos los módulos de Phase 2

### Archivos a Eliminar
- [ ] `src/shared/infra/di.py` (archivo completo)

### Archivos a Modificar
- [ ] `src/__init__.py`
  - Eliminar `init_mappers()`
  - Eliminar `init_repositories()`
  - Eliminar `init_handlers()`
  - Eliminar `init_controllers()`
  - Eliminar `initialize()`
  - Eliminar `get_request_scope_id()`
  - Eliminar todas las funciones `get_*_controller()` restantes
  - Eliminar imports: `DependencyContainer`, `LifetimeScope`
  - Eliminar variable global `container`

- [ ] `main.py`
  - Eliminar llamada a `initialize()`
  - Limpiar imports obsoletos

### LoC a Eliminar
- ~200 líneas (funciones init_* + di.py)

### Verificación Final
```bash
# Tests completos
pytest tests/ -v --cov=src --cov-report=term-missing

# Performance benchmark
# (comparar tiempo de startup y request latency vs baseline)

# Validación de startup
python main.py
# → Debe detectar cualquier error de dependencias al inicio
```

---

## 📈 Progreso por Sesión

### Sesión 1 (2026-02-11)
- ✅ Phase 0 completa
- ✅ Phase 1 completa (Category)
- 📝 Documentación creada

**Próxima sesión:** Migrar Product module

---

## 🎯 Objetivos de Próximas Sesiones

### Sesión 2: Product + Movement
- [ ] Migrar módulo Product
- [ ] Migrar módulo Movement
- [ ] Commit de ambos módulos

### Sesión 3: Stock + CustomerContact
- [ ] Migrar módulo Stock
- [ ] Migrar módulo CustomerContact
- [ ] Commit de ambos módulos

### Sesión 4: Customer
- [ ] Migrar módulo Customer
- [ ] Tests exhaustivos
- [ ] Commit

### Sesión 5: Sale
- [ ] Migrar módulo Sale (complejo, requiere atención)
- [ ] Tests exhaustivos
- [ ] Commit

### Sesión 6: Cleanup
- [ ] Phase 3 completa
- [ ] Verificación final
- [ ] Performance testing
- [ ] Commit final

---

## 📋 Comandos Rápidos

### Iniciar trabajo en un módulo
```bash
git checkout -b feat/wireup-migration-{module}
```

### Verificar después de modificar
```bash
# Quick check
.venv/bin/python -c "from main import app; print('✓ OK')"

# Run tests
.venv/bin/python -m pytest tests/unit/{module}/ -v
```

### Commit
```bash
git add .
git commit -m "feat: migrate {module} module to wireup DI"
git checkout master
git merge feat/wireup-migration-{module}
```

---

## 🔗 Referencias

- [Guía Completa de Migración](./WIREUP_MIGRATION_GUIDE.md)
- [Plan Original](../.claude/projects/-Users-dbsiavichay-Workspace-Faclab-faclab-core/78676b5b-44c1-471e-8156-a99a58349b12.jsonl)
- [Wireup Docs](https://maldoinc.github.io/wireup/latest/)
