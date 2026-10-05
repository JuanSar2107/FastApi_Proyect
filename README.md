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

## Ejecutar con Docker

```bash
docker compose up --build
```

La API estará disponible en **http://localhost:8000** y la documentación en
**http://localhost:8000/docs**. La base de datos SQLite se guarda en un volumen
de Docker para conservar los datos al reiniciar el contenedor.

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
├── main.py
├── config.py
├── database.py
├── auth.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── category.py
│   ├── supplier.py
│   ├── product.py
│   └── inventory_movement.py
├── schemas/
│   ├── __init__.py
│   ├── auth.py
│   ├── users.py
│   ├── categories.py
│   ├── suppliers.py
│   ├── products.py
│   ├── inventory.py
│   └── reports.py
└── routers/
    ├── auth.py
    ├── users.py
    ├── categories.py
    ├── suppliers.py
    ├── products.py
    ├── inventory.py
    └── reports.py
```

Los modelos ORM y esquemas de validación están separados por entidad. Los imports
existentes desde `app.models` y `app.schemas` se conservan mediante sus archivos
`__init__.py`, por lo que las rutas y los scripts actuales no necesitan cambiar.

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
