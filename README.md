# Faclab Core - Sistema de Ventas e Inventarios

Un sistema completo de ventas e inventarios construido con FastAPI y principios de arquitectura limpia. Esta API proporciona funcionalidad integral para gestionar todo el ciclo de ventas, desde el catálogo de productos hasta el control de inventarios y la administración de clientes.

## Características

- **Gestión de Catálogo**
  - Administración completa de productos con seguimiento de SKU
  - Organización por categorías
  - Control de precios y descripciones

- **Control de Inventarios**
  - Seguimiento en tiempo real de niveles de stock por producto y ubicación
  - Registro de movimientos de inventario (entradas/salidas)
  - Trazabilidad completa de transacciones

- **Gestión de Clientes**
  - Perfiles de clientes y información detallada
  - Administración de contactos de clientes
  - Historial de relaciones comerciales

- **Sistema de Ventas** *(En desarrollo)*
  - Procesamiento de órdenes y cotizaciones
  - Facturación y documentos fiscales
  - Reportes y análisis de ventas

- **Arquitectura Limpia**
  - Separación clara de responsabilidades (capas de dominio, aplicación e infraestructura)
  - Contenedor de inyección de dependencias con gestión de ciclo de vida
  - Patrones Repository y Mapper

## Stack Tecnológico

- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Servidor**: Uvicorn
- **Contenedores**: Docker & Docker Compose
- **Testing**: Pytest
- **Calidad de Código**: Black, isort, Flake8
- **Observabilidad**: OpenTelemetry, Structlog

## Requisitos Previos

- Docker y Docker Compose (recomendado)
- Python 3.11+ (para desarrollo local)
- PostgreSQL (si se ejecuta localmente sin Docker)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Faclab/faclab-core.git
cd faclab-core
```

2. Configurar variables de entorno:
```bash
# Crear un archivo .env con la cadena de conexión a la base de datos
echo "DB_CONNECTION_STRING=postgresql://user:password@localhost:5432/faclab_db" > .env
echo "ENVIRONMENT=local" >> .env
```

## Ejecución de la Aplicación

### Usando Docker (Recomendado)

Iniciar el servidor de desarrollo con auto-recarga:
```bash
make dev
```

La API estará disponible en `http://localhost:3000` y redirigirá automáticamente a la documentación Swagger en `http://localhost:3000/docs`.

### Desarrollo Local

1. Crear y activar un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python main.py
```

## Comandos de Desarrollo

### Operaciones Docker

```bash
make build          # Construir imágenes Docker
make start          # Iniciar contenedores en modo separado
make dev            # Iniciar servidor de desarrollo con hot reload
make down           # Detener y eliminar contenedores
```

### Migraciones de Base de Datos

```bash
# Crear una nueva migración
make migrations m="agregar campo a productos"

# Aplicar todas las migraciones pendientes
make upgrade

# Revertir a una migración específica
make downgrade d=revision_id
```

### Testing y Calidad de Código

```bash
# Ejecutar tests con cobertura
make tests

# Formatear y validar código (requiere venv local)
make lint
```

## Estructura del Proyecto

```
faclab-core/
├── src/
│   ├── core/                      # Infraestructura compartida
│   │   ├── domain/                # Clases base de entidades
│   │   ├── app/                   # Interfaces de repositorios
│   │   └── infra/                 # Contenedor DI, repositorio base, sesión DB
│   ├── catalog/
│   │   └── product/               # Módulos de productos y categorías
│   ├── inventory/
│   │   ├── stock/                 # Seguimiento de stock
│   │   └── movement/              # Movimientos de inventario
│   ├── customers/                 # Gestión de clientes
│   └── sales/                     # Sistema de ventas (próximamente)
├── config/                        # Configuraciones por entorno
├── alembic/                       # Migraciones de base de datos
├── main.py                        # Punto de entrada de la aplicación
└── Makefile                       # Comandos de desarrollo
```

Cada módulo de dominio sigue arquitectura limpia:
```
module/
├── domain/         # Entidades (dataclasses inmutables)
├── app/            # Casos de uso (lógica de negocio)
└── infra/          # Controladores, rutas, repositorios, modelos, mappers
```

## Documentación de la API

Una vez que la aplicación esté en ejecución, la documentación interactiva de la API está disponible en:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## Aspectos Destacados de la Arquitectura

### Inyección de Dependencias

La aplicación utiliza un contenedor DI personalizado con tres alcances:
- **SINGLETON**: Instancias compartidas (mappers)
- **SCOPED**: Ciclo de vida por petición (repositorios, casos de uso, controladores, sesiones DB)
- **TRANSIENT**: Nueva instancia por resolución

### Flujo de Peticiones

```
Petición HTTP → Ruta → Controlador → Caso de Uso → Repositorio → Base de Datos
```

Cada petición obtiene un alcance único donde todos los componentes comparten la misma sesión de base de datos, asegurando consistencia transaccional.

### Patrones Clave

- **Patrón Repository**: Operaciones CRUD genéricas con `BaseRepository[Entity]`
- **Patrón Mapper**: Conversión bidireccional entre entidades de dominio y modelos SQLAlchemy
- **Patrón Use Case**: Encapsulación de lógica de negocio

## Configuración

La aplicación soporta múltiples entornos a través de archivos de configuración:

- `config/local.py` - Desarrollo local
- `config/staging.py` - Entorno de staging
- `config/production.py` - Entorno de producción

Establecer la variable `ENVIRONMENT` para cambiar entre configuraciones. La cadena de conexión a la base de datos debe proporcionarse mediante la variable de entorno `DB_CONNECTION_STRING`.


## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para más detalles.

---

**Desarrollado por Faclab**
