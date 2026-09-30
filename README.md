# Sistema de Gestión de Inventarios - API

Backend en FastAPI para gestión de inventarios de una empresa.

## Requisitos

- Python 3.10+

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación interactiva

Una vez corriendo, abre: **http://localhost:8000/docs**

## Datos de prueba

```bash
python seed.py
```

| Usuario  | Contraseña   | Rol   |
|----------|--------------|-------|
| admin    | admin123     | admin |
| vendedor | vendedor123  | user  |

## Estructura del proyecto

```
app/
├── main.py           # Punto de entrada FastAPI
├── config.py         # Configuración (Pydantic Settings)
├── database.py       # Sesión SQLAlchemy
├── models.py         # Modelos ORM
├── schemas.py        # Esquemas Pydantic (request/response)
├── auth.py           # JWT, hashing, dependencias de seguridad
└── routers/
    ├── auth.py       # Login, registro, /me
    ├── users.py      # CRUD usuarios (solo admin)
    ├── categories.py # CRUD categorías
    ├── suppliers.py  # CRUD proveedores
    ├── products.py   # CRUD productos
    ├── inventory.py  # Movimientos (entrada/salida/ajuste)
    └── reports.py    # Reportes (stock bajo, resumen)
```

## Endpoints principales

| Método | Ruta                        | Descripción                        |
|--------|-----------------------------|------------------------------------|
| POST   | /api/auth/login             | Login (formulario OAuth2)          |
| POST   | /api/auth/login/json        | Login (JSON)                       |
| POST   | /api/auth/register          | Registro de usuario                |
| GET    | /api/auth/me                | Usuario actual                     |
| GET    | /api/users                  | Listar usuarios (admin)            |
| POST   | /api/users                  | Crear usuario (admin)              |
| GET    | /api/categories             | Listar categorías                  |
| POST   | /api/categories             | Crear categoría                    |
| GET    | /api/suppliers              | Listar proveedores                 |
| POST   | /api/suppliers              | Crear proveedor                    |
| GET    | /api/products               | Listar productos (con filtros)     |
| POST   | /api/products               | Crear producto                     |
| POST   | /api/inventory/movements   | Registrar movimiento               |
| GET    | /api/inventory/movements   | Historial de movimientos           |
| GET    | /api/reports/low-stock      | Productos con stock bajo           |
| GET    | /api/reports/summary        | Resumen general del inventario     |
```

## Notas

- Autenticación con JWT (Bearer token)
- Contraseñas hasheadas con bcrypt
- Soft delete en productos
- Validación de stock antes de salidas
- SQLite por defecto (configurable vía `DATABASE_URL`)
