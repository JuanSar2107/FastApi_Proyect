"""Script para poblar la base de datos con datos de prueba."""
from app.auth import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import Category, InventoryMovement, Product, Supplier, User

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Usuarios
admin = User(
    username="admin",
    email="admin@inventario.com",
    full_name="Administrador",
    role="admin",
    hashed_password=get_password_hash("admin123"),
)
user = User(
    username="vendedor",
    email="vendedor@inventario.com",
    full_name="Vendedor Demo",
    role="user",
    hashed_password=get_password_hash("vendedor123"),
)
db.add_all([admin, user])

# Categorías
cats = [
    Category(name="Electrónica", description="Dispositivos electrónicos"),
    Category(name="Alimentos", description="Productos alimenticios"),
    Category(name="Limpieza", description="Productos de limpieza"),
    Category(name="Oficina", description="Papelería y útiles de oficina"),
]
db.add_all(cats)
db.flush()

# Proveedores
suppliers = [
    Supplier(name="TechCorp", contact_name="Juan Pérez", email="juan@techcorp.com", phone="555-0101"),
    Supplier(name="Distribuidora Sur", contact_name="María López", email="maria@distsur.com", phone="555-0202"),
    Supplier(name="LimpiezaTotal", contact_name="Carlos Ruiz", email="carlos@limpiezatotal.com", phone="555-0303"),
]
db.add_all(suppliers)
db.flush()

# Productos
products = [
    Product(name="Laptop HP 15", sku="ELEC-001", category_id=1, supplier_id=1, price=899.99, cost=650.00, stock_quantity=15, min_stock=5),
    Product(name="Mouse Inalámbrico", sku="ELEC-002", category_id=1, supplier_id=1, price=25.50, cost=12.00, stock_quantity=50, min_stock=10),
    Product(name="Teclado Mecánico", sku="ELEC-003", category_id=1, supplier_id=1, price=75.00, cost=40.00, stock_quantity=3, min_stock=5),
    Product(name="Arroz 1kg", sku="ALIM-001", category_id=2, supplier_id=2, price=1.20, cost=0.80, stock_quantity=200, min_stock=50),
    Product(name="Aceite de Oliva 500ml", sku="ALIM-002", category_id=2, supplier_id=2, price=8.50, cost=5.00, stock_quantity=80, min_stock=20),
    Product(name="Detergente 1L", sku="LIMP-001", category_id=3, supplier_id=3, price=3.50, cost=2.00, stock_quantity=100, min_stock=30),
    Product(name="Papel A4 (resma)", sku="OFIC-001", category_id=4, supplier_id=2, price=5.00, cost=3.50, stock_quantity=60, min_stock=15),
]
db.add_all(products)
db.flush()

# Movimientos de ejemplo
movements = [
    InventoryMovement(product_id=1, user_id=1, movement_type="entry", quantity=20, previous_stock=0, new_stock=20, reason="Compra inicial"),
    InventoryMovement(product_id=1, user_id=1, movement_type="exit", quantity=5, previous_stock=20, new_stock=15, reason="Venta #001"),
    InventoryMovement(product_id=3, user_id=1, movement_type="entry", quantity=10, previous_stock=0, new_stock=10, reason="Compra inicial"),
    InventoryMovement(product_id=3, user_id=1, movement_type="exit", quantity=7, previous_stock=10, new_stock=3, reason="Venta #002"),
]
db.add_all(movements)

db.commit()
db.close()

print("✅ Datos de prueba insertados correctamente.")
print("   Usuarios: admin/admin123 (admin), vendedor/vendedor123 (user)")
