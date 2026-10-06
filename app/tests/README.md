# Pruebas de software

Esta carpeta contiene pruebas automatizadas de la API: autenticación y permisos,
validación de datos, operaciones CRUD, productos, movimientos de inventario y
reportes. Cada prueba usa una base SQLite temporal aislada.

Instala las dependencias de desarrollo desde la raíz del proyecto con
`pip install -r requirements-dev.txt` y ejecuta la suite con `pytest app/test`.
