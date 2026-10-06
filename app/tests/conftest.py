import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import Category, Product, Supplier, User


@pytest.fixture
def db_session():
    """Una base SQLite aislada para cada prueba."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """Cliente de API con la dependencia de base de datos reemplazada."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # No usar el administrador de contexto: evita iniciar el lifespan de
    # producción y crear tablas en la base configurada para desarrollo.
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(db_session):
    def create_user(username="tester", email=None, password="secret123", role="user", is_active=1):
        user = User(
            username=username,
            email=email or f"{username}@example.com",
            hashed_password=get_password_hash(password),
            full_name="Usuario de prueba",
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def auth_headers(client, user_factory):
    user = user_factory()
    response = client.post("/api/auth/login/json", json={"username": user.username, "password": "secret123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client, user_factory):
    user = user_factory(username="admin", role="admin")
    response = client.post("/api/auth/login/json", json={"username": user.username, "password": "secret123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def catalog_factory(db_session):
    def create_catalog(stock=10, min_stock=2, active=1):
        category = Category(name="General", description="Categoría de prueba")
        supplier = Supplier(name="Proveedor de prueba", email="proveedor@example.com")
        db_session.add_all([category, supplier])
        db_session.flush()
        product = Product(
            name="Producto de prueba",
            sku="SKU-TEST",
            category_id=category.id,
            supplier_id=supplier.id,
            price=15.5,
            cost=7.25,
            stock_quantity=stock,
            min_stock=min_stock,
            is_active=active,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return category, supplier, product

    return create_catalog
