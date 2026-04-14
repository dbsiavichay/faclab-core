# Auth & Authorization Plan — Faclab Core

## Context

Faclab Core expone toda su API (admin y POS) sin autenticación. Se necesita un módulo propio (`src/auth/`) que agregue:

- **Autenticación** con JWT **HS256** (decisión del usuario sobre RS256 — monolito, sin servicios externos verificando tokens, un solo `JWT_SECRET` en env es lo pragmático).
- **Access + refresh tokens** (access ~15 min, refresh ~7 días).
- **Roles y permisos hardcoded en código** — enum `Role` + mapa estático `Role → frozenset[Permission]`. Sin tablas extras, sin UI de gestión.
- **Bootstrap del primer admin** vía comando CLI de seed (sin endpoint público de registro).

El diseño reusa al 100% los patrones ya presentes en el proyecto (Clean Architecture + CQRS + wireup + mappers convencionales + `ErrorHandlingMiddleware` + `Meta`/`get_meta`). El módulo se llama `src/auth/` y es paralelo a `src/customers/` en estructura.

## Decisiones clave

| Tema | Decisión |
|---|---|
| Algoritmo JWT | HS256, `JWT_SECRET` en env/config |
| Tokens | Access (15 min) + Refresh (7 días), ambos firmados con el mismo secreto pero con `claim typ` distinto (`access` / `refresh`) |
| Password hashing | `passlib[bcrypt]` (estándar, sin dependencias C pesadas) |
| Modelo de permisos | `Role` (enum int) en tabla `users`; `PERMISSIONS_BY_ROLE: dict[Role, frozenset[Permission]]` hardcoded |
| Primer admin | `python -m src.auth.seed` leyendo `AUTH_SEED_USERNAME`, `AUTH_SEED_EMAIL`, `AUTH_SEED_PASSWORD` |
| Almacenamiento de refresh tokens | Stateless (no DB). Rotación simple en `/auth/refresh`. Sin blacklist en v1. |
| Storage del token en frontend | Responsabilidad del cliente — API solo devuelve el par |
| Endpoints protegidos | Por defecto público en v1; se aplica `require_permission(...)` módulo por módulo en sesiones posteriores. El plan solo cubre el cableado — no migra routers existentes en masa. |

## Patrones existentes a reusar (no reinventar)

Verificados en exploración inicial:

- **Entity base**: `src/shared/domain/entities.py` — `Entity` con `.dict()`.
- **ValueObject**: `src/shared/domain/value_objects.py` — frozen dataclass con `_validate()`. Usar para `Email` (ya existe) y definir `HashedPassword`, `PlainPassword`.
- **Errores**: `src/shared/domain/exceptions.py` — `DomainError`, `ApplicationError`, `NotFoundError`, `ValidationError`. Subclasear para `InvalidCredentialsError`, `TokenExpiredError`, `PermissionDeniedError` (401/401/403 respectivamente — extender `ErrorHandlingMiddleware` si aún no mapea 401/403).
- **Command/Query bases**: `src/shared/app/commands.py`, `src/shared/app/queries.py`.
- **Repositorio**: `SqlAlchemyRepository[E]` en `src/shared/infra/repositories.py` — declarar `__model__ = UserModel`.
- **Mapper**: `src/shared/infra/mappers.py` — convención `__entity__` + `__exclude_fields__`.
- **Meta / request_id**: `src/shared/infra/dependencies.py::get_meta`, poblado por `ErrorHandlingMiddleware` en `request.state.request_id`. Se extiende para poblar `request.state.current_user`.
- **Container**: cada módulo expone `INJECTABLES` en `infra/container.py`; se mergean en `src/container.py::create_wireup_container()`.
- **Router pattern**: `src/customers/infra/routes.py` — clase `CustomerRouter`, `_setup_routes()`, handlers con `Injected[...]` + `Depends(get_meta)`. Copiar estructura.
- **Docs split**: `main.py` filtra por prefijo. `/api/auth/*` con `tags=["Auth"]` aparece en `/docs` principal; si se quiere ocultar de `/docs/pos` montarlo bajo `/api/admin/auth`. **Decisión**: bajo `/api/auth` (login lo usan tanto admin como POS).

## Dependencias nuevas a agregar

En `requirements.txt`:

```
PyJWT==2.9.0
passlib[bcrypt]==1.7.4
```

(No `python-jose` — `PyJWT` es más liviano y suficiente para HS256.)

## Config (nuevas variables)

Añadir en `config/local.py`, `config/staging.py`, `config/production.py`:

```python
JWT_SECRET: str = env.str("JWT_SECRET")
JWT_ACCESS_TTL_SECONDS: int = env.int("JWT_ACCESS_TTL_SECONDS", 900)       # 15 min
JWT_REFRESH_TTL_SECONDS: int = env.int("JWT_REFRESH_TTL_SECONDS", 604800)  # 7 días
JWT_ISSUER: str = env.str("JWT_ISSUER", "faclab-core")
```

Documentar en `.env.example` si existe. **En `local.py` dar un default obviamente-dev** (`"dev-only-change-me"`) para no romper `make dev`.

---

## Estructura del módulo `src/auth/`

```
src/auth/
├── domain/
│   ├── entities.py          # User, Role (enum), Permission (enum)
│   ├── permissions.py       # PERMISSIONS_BY_ROLE: dict[Role, frozenset[Permission]]
│   ├── value_objects.py     # HashedPassword, PlainPassword
│   ├── events.py            # UserCreated, UserLoggedIn, UserPasswordChanged
│   └── exceptions.py        # InvalidCredentialsError, TokenExpiredError, InvalidTokenError, PermissionDeniedError
├── app/
│   ├── services/
│   │   ├── password_hasher.py   # PasswordHasher (passlib bcrypt wrapper) — interface en domain, impl en infra
│   │   └── token_service.py     # TokenService — encode/decode JWT, refresh rotation
│   ├── commands/
│   │   ├── login.py             # LoginCommand + LoginCommandHandler -> TokenPair
│   │   ├── refresh_token.py     # RefreshTokenCommand + handler -> TokenPair
│   │   ├── create_user.py       # CreateUserCommand + handler (usado por seed y por admin)
│   │   └── change_password.py   # ChangePasswordCommand + handler
│   └── queries/
│       └── get_current_user.py  # GetCurrentUserQuery -> UserDto (usado por /auth/me)
├── infra/
│   ├── models.py            # UserModel (SQLAlchemy)
│   ├── mappers.py           # UserMapper
│   ├── repositories.py      # SqlAlchemyUserRepository con __model__ = UserModel
│   ├── password_hasher.py   # BcryptPasswordHasher
│   ├── token_service.py     # JwtTokenService (HS256, PyJWT)
│   ├── middleware.py        # AuthMiddleware — lee Bearer token, puebla request.state.current_user
│   ├── dependencies.py      # get_current_user, require_permission(*perms), get_optional_user
│   ├── validators.py        # LoginRequest, TokenPairResponse, UserResponse, etc.
│   ├── routes.py            # AuthRouter: /login, /refresh, /me, /change-password
│   └── container.py         # INJECTABLES
└── seed.py                  # python -m src.auth.seed — bootstrap del admin inicial
```

### Detalles del dominio

`domain/entities.py`:

```python
class Role(IntEnum):
    ADMIN = 1
    MANAGER = 2
    OPERATOR = 3
    VIEWER = 4

@dataclass(frozen=True)
class User(Entity):
    id: int | None
    username: str
    email: Email
    password_hash: HashedPassword
    role: Role
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

`domain/permissions.py`:

```python
class Permission(str, Enum):
    # Catalog
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    # Inventory
    STOCK_READ = "stock:read"
    MOVEMENT_WRITE = "movement:write"
    # Sales
    SALE_READ = "sale:read"
    SALE_WRITE = "sale:write"
    SALE_CANCEL = "sale:cancel"
    # Users / admin
    USER_MANAGE = "user:manage"
    # ... agregar por módulo según se necesite

PERMISSIONS_BY_ROLE: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),  # todos
    Role.MANAGER: frozenset({
        Permission.PRODUCT_READ, Permission.PRODUCT_WRITE,
        Permission.STOCK_READ, Permission.MOVEMENT_WRITE,
        Permission.SALE_READ, Permission.SALE_WRITE, Permission.SALE_CANCEL,
    }),
    Role.OPERATOR: frozenset({
        Permission.PRODUCT_READ, Permission.STOCK_READ,
        Permission.SALE_READ, Permission.SALE_WRITE,
    }),
    Role.VIEWER: frozenset({
        Permission.PRODUCT_READ, Permission.STOCK_READ, Permission.SALE_READ,
    }),
}

def permissions_for(role: Role) -> frozenset[Permission]:
    return PERMISSIONS_BY_ROLE[role]
```

La lista inicial es intencionalmente mínima — se extiende a medida que se cubren módulos.

### TokenService (interface en `app/services`, impl en `infra`)

Interfaz:

```python
class TokenService(ABC):
    @abstractmethod
    def issue_pair(self, user: User) -> TokenPair: ...
    @abstractmethod
    def decode_access(self, token: str) -> TokenClaims: ...
    @abstractmethod
    def decode_refresh(self, token: str) -> TokenClaims: ...
```

Claims mínimas: `sub` (user id), `username`, `role` (int), `typ` (`access`|`refresh`), `iat`, `exp`, `iss`. **No** embebemos permisos en el token — se resuelven server-side por rol en cada request (fuente única de verdad, cambios de permisos no requieren reemitir tokens).

`JwtTokenService` usa `PyJWT`, lee `JWT_SECRET`, TTLs e `iss` del settings (inyectado vía wireup como SCOPED o SINGLETON — SINGLETON está bien, es stateless).

### Middleware

`AuthMiddleware` (nuevo, registrado **después** de `ErrorHandlingMiddleware` y antes de CORS en `main.py`):

1. Si no hay header `Authorization: Bearer <token>` → no hace nada (`request.state.current_user = None`).
2. Si hay token → decodifica como access token. Si falla → responde 401 con `error_code="invalid_token"`.
3. Si ok → setea `request.state.current_user = AuthenticatedUser(id, username, role, permissions)`.
4. Rutas públicas (login, refresh, `/docs*`, `/health`) se saltan la verificación — lista de prefijos en constructor.

El middleware **no obliga** autenticación — eso lo hace la dependencia `get_current_user`. Esto permite rutas públicas sin tocar el middleware.

### Dependencias FastAPI

```python
def get_current_user(request: Request) -> AuthenticatedUser:
    user = getattr(request.state, "current_user", None)
    if user is None:
        raise PermissionDeniedError("authentication required")
    return user

def require_permission(*required: Permission):
    def _dep(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not set(required).issubset(user.permissions):
            raise PermissionDeniedError(f"missing permissions: {required}")
        return user
    return _dep
```

### Endpoints (`AuthRouter`, prefijo `/api/auth`)

| Método | Path | Body | Respuesta | Protección |
|---|---|---|---|---|
| POST | `/login` | `{username, password}` | `{access_token, refresh_token, token_type, expires_in}` | público |
| POST | `/refresh` | `{refresh_token}` | `{access_token, refresh_token, ...}` | público (valida token) |
| GET  | `/me` | — | `UserResponse` | `get_current_user` |
| POST | `/change-password` | `{current_password, new_password}` | 204 | `get_current_user` |

(`POST /users` para crear usuarios se agrega en sesión 3 bajo `/api/admin/users` con `require_permission(USER_MANAGE)`, no en `/auth`.)

### Migración

```bash
make migrations m="create users table"
```

Tabla `users` con: `id` (PK int autoincrement — consistente con el resto del repo), `username` (unique, indexed), `email` (unique, indexed), `password_hash` (String 255), `role` (Integer, index), `is_active` (Boolean default true), `last_login_at` (DateTime nullable), `created_at`, `updated_at` (timestamps estándar como otros modelos).

### Seed CLI

`src/auth/seed.py`:

```python
# python -m src.auth.seed
# Lee AUTH_SEED_USERNAME, AUTH_SEED_EMAIL, AUTH_SEED_PASSWORD del env.
# Si el usuario ya existe, no hace nada (idempotente).
# Usa CreateUserCommandHandler vía wireup para reusar la validación.
```

Añadir target en `Makefile`: `make seed-admin`.

---

## Plan por sesiones

### Sesión 1 — Fundación del módulo (users + hashing + migración)

**Objetivo:** tener usuarios en DB, hash de contraseñas, seed funcional. Aún no hay login.

1. Agregar `PyJWT` y `passlib[bcrypt]` a `requirements.txt`; `make build`.
2. Añadir `JWT_SECRET`, `JWT_*_TTL_SECONDS`, `JWT_ISSUER` a los tres `config/*.py`.
3. Crear esqueleto `src/auth/` con subcarpetas vacías `__init__.py`.
4. `domain/entities.py` → `User`, `Role`, `AuthenticatedUser` (DTO in-memory, no dataclass de Entity).
5. `domain/permissions.py` → `Permission` enum + `PERMISSIONS_BY_ROLE` (versión mínima).
6. `domain/value_objects.py` → `HashedPassword`, `PlainPassword` (con `_validate()` — min length 8).
7. `domain/exceptions.py` → `InvalidCredentialsError`, `TokenExpiredError`, `InvalidTokenError`, `PermissionDeniedError`. Extender `ErrorHandlingMiddleware` (`src/shared/infra/middlewares.py`) para mapear las dos últimas a 401/403 si no lo hace aún.
8. `infra/models.py` → `UserModel`.
9. `infra/mappers.py` → `UserMapper` con `__entity__ = User`, `__exclude_fields__ = {"created_at", "updated_at"}`.
10. `infra/repositories.py` → `SqlAlchemyUserRepository(__model__ = UserModel)` + métodos `get_by_username`, `get_by_email`.
11. `infra/password_hasher.py` → `BcryptPasswordHasher` (SINGLETON). Interfaz en `app/services/password_hasher.py`.
12. `app/commands/create_user.py` → `CreateUserCommand` + handler. Valida unicidad username/email, hashea, persiste, publica `UserCreated`.
13. `infra/container.py` → `INJECTABLES` con repo (SCOPED), hasher (SINGLETON), mapper (SINGLETON), `CreateUserCommandHandler` (SCOPED).
14. Registrar en `src/container.py::create_wireup_container()`.
15. `src/auth/seed.py` + `make seed-admin`.
16. Migración `make migrations m="create users table"` + `make upgrade`.
17. **Verificar**: `make seed-admin` crea admin; consulta SQL directa confirma registro con password hasheado (no plano).

### Sesión 2 — Login, JWT y middleware

**Objetivo:** flujo completo login → token → `/auth/me` protegido.

1. `app/services/token_service.py` → interfaz `TokenService` + `TokenPair`, `TokenClaims` dataclasses.
2. `infra/token_service.py` → `JwtTokenService` (PyJWT HS256, lee settings). Registrar como SINGLETON.
3. `app/commands/login.py` → `LoginCommandHandler`: busca por username, valida hash, actualiza `last_login_at`, publica `UserLoggedIn`, emite par de tokens.
4. `app/commands/refresh_token.py` → decodifica refresh, valida `typ`, recarga user desde DB (para capturar `is_active=false` y cambios de rol), emite par nuevo.
5. `infra/validators.py` → Pydantic schemas.
6. `infra/middleware.py` → `AuthMiddleware` (skip paths: `/api/auth/login`, `/api/auth/refresh`, `/docs*`, `/openapi.json`, `/health`).
7. `infra/dependencies.py` → `get_current_user`, `get_optional_user`, `require_permission(*perms)`.
8. `infra/routes.py` → `AuthRouter` con `/login`, `/refresh`, `/me`, `/change-password`.
9. `main.py` → montar `AuthRouter` en `/api/auth` (tag `"Auth"`), añadir `AuthMiddleware` entre `ErrorHandlingMiddleware` y `CORSMiddleware`.
10. Tests unitarios para `JwtTokenService` (encode/decode round-trip, expiración, tipo equivocado, firma inválida) y `LoginCommandHandler` (credenciales válidas/inválidas, usuario inactivo).
11. **Verificar end-to-end**:
    - `make dev`
    - `curl -X POST /api/auth/login` con seed → recibe par de tokens
    - `curl /api/auth/me` con `Authorization: Bearer …` → 200 con datos del usuario
    - Sin header → 401
    - Token expirado (TTL=2s temporal) → 401 `token_expired`
    - Refresh con refresh token → nuevo par
    - Refresh con access token → 401 `invalid_token`

### Sesión 3 — Autorización (permisos) y gestión de usuarios

**Objetivo:** permisos aplicables a rutas + CRUD básico de usuarios para admin.

1. `app/commands/change_password.py` + ruta (si quedó pendiente).
2. `app/commands/update_user_role.py`, `deactivate_user.py`, `activate_user.py`.
3. `app/queries/list_users.py`, `get_user_by_id.py`.
4. Crear `src/auth/infra/admin_routes.py` con `UserAdminRouter`: `GET/POST/PUT /api/admin/users/...` todas protegidas con `require_permission(Permission.USER_MANAGE)`. Montar en `main.py` bajo `/api/admin` con tag `"Users"`.
5. **Aplicar `require_permission` a rutas existentes críticas como ejemplo** (no migrar todo el proyecto — solo dejar el patrón establecido en 2-3 módulos piloto: `sales` (`SALE_WRITE`, `SALE_CANCEL`), `products` (`PRODUCT_WRITE`). El resto se migra incrementalmente fuera del plan.
6. Extender `PERMISSIONS_BY_ROLE` con los permisos reales de los módulos migrados.
7. Tests de integración: usuario VIEWER recibe 403 en endpoints de escritura; ADMIN pasa en todos.
8. Documentar en `docs/` un `auth-spec.md` breve (1 página): cómo obtener token, cómo proteger una ruta (`require_permission(...)`), cómo añadir un nuevo permiso.
9. **Verificar**:
    - Crear usuario operator vía `/api/admin/users` como admin → 201
    - Mismo usuario intentando crear otro usuario → 403
    - Operator puede `POST /api/admin/sales` → 200; no puede `POST /api/admin/sales/{id}/cancel` → 403
    - `make tests` pasa; `make lint` limpio

---

## Archivos críticos a crear/modificar

**Nuevos** (`src/auth/**`):
- `src/auth/__init__.py`
- `src/auth/domain/{entities,permissions,value_objects,events,exceptions}.py`
- `src/auth/app/services/{password_hasher,token_service}.py`
- `src/auth/app/commands/{create_user,login,refresh_token,change_password,update_user_role,deactivate_user,activate_user}.py`
- `src/auth/app/queries/{get_current_user,list_users,get_user_by_id}.py`
- `src/auth/infra/{models,mappers,repositories,password_hasher,token_service,middleware,dependencies,validators,routes,admin_routes,container}.py`
- `src/auth/seed.py`
- `alembic/versions/<hash>_create_users_table.py`
- `docs/auth-spec.md`

**Modificados**:
- `requirements.txt` — agregar `PyJWT`, `passlib[bcrypt]`
- `config/local.py`, `config/staging.py`, `config/production.py` — variables JWT
- `src/container.py` — merge `AUTH_INJECTABLES`
- `src/shared/infra/middlewares.py` — mapear 401/403 si faltan
- `main.py` — registrar `AuthRouter`, `UserAdminRouter`, `AuthMiddleware`
- `Makefile` — target `seed-admin`

**Paths de rutas piloto a proteger en sesión 3** (confirmar al llegar):
- `src/sales/infra/routes.py`
- `src/catalog/product/infra/routes.py`

---

## Verificación end-to-end (al final de las 3 sesiones)

```bash
# 1. Build + migración + seed
make build && make upgrade
AUTH_SEED_USERNAME=admin AUTH_SEED_EMAIL=admin@faclab.local \
  AUTH_SEED_PASSWORD=ChangeMe123! make seed-admin

# 2. Levantar
make dev

# 3. Login
curl -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"ChangeMe123!"}'
# → {access_token, refresh_token, ...}

# 4. /me
curl http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer <access>"
# → 200 con role=1 (ADMIN)

# 5. Sin token
curl http://localhost:3000/api/auth/me
# → 401 authentication_required

# 6. Refresh
curl -X POST http://localhost:3000/api/auth/refresh \
  -H 'Content-Type: application/json' -d '{"refresh_token":"<refresh>"}'
# → nuevo par

# 7. Crear operator como admin
curl -X POST http://localhost:3000/api/admin/users \
  -H "Authorization: Bearer <admin-access>" \
  -d '{"username":"op1","email":"op1@f.lo","password":"secret12","role":3}'

# 8. Login como operator → intentar cancelar venta → 403
# 9. make tests && make lint
```

Pruebas automatizadas mínimas a añadir en `tests/`:

- `tests/unit/auth/test_token_service.py` — round-trip, expiración, tipo equivocado, firma inválida.
- `tests/unit/auth/test_password_hasher.py` — verify true/false, rehash.
- `tests/unit/auth/test_permissions.py` — cada rol tiene los permisos esperados.
- `tests/integration/auth/test_login_flow.py` — login→/me→refresh→/me con cliente FastAPI.
- `tests/integration/auth/test_require_permission.py` — viewer 403, admin 200 en endpoint piloto.

## Fuera de alcance (explícitamente)

Para mantener 2-3 sesiones y evitar sobreingeniería, **no** se incluye:

- Blacklist / revocación de tokens (logout stateful)
- Refresh token rotation con detección de reuso (familia de tokens)
- MFA / 2FA / OAuth social / magic links
- Recuperación de contraseña por email
- Rate limiting de login (se añade a nivel middleware global fuera de este plan)
- Auditoría completa de eventos de seguridad (solo se publica `UserLoggedIn`, sin handler inicial)
- UI de administración de usuarios (solo API)
- Migración masiva de todos los routers existentes a `require_permission` — solo 2 módulos piloto
