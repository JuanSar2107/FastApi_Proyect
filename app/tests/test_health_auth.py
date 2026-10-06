def test_root_and_health_are_available_without_auth(client):
    assert client.get("/").json()["docs"] == "/docs"
    assert client.get("/health").json() == {"status": "ok"}


def test_protected_route_requires_token(client):
    response = client.get("/api/categories")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_register_and_login_json(client):
    payload = {
        "username": "nuevo",
        "email": "nuevo@example.com",
        "full_name": "Nuevo Usuario",
        "password": "clave123",
    }
    registered = client.post("/api/auth/register", json=payload)
    assert registered.status_code == 201
    assert registered.json()["username"] == "nuevo"
    assert "hashed_password" not in registered.json()

    login = client.post("/api/auth/login/json", json={"username": "nuevo", "password": "clave123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_register_rejects_duplicate_username_and_email(client):
    payload = {"username": "duplicado", "email": "dup@example.com", "password": "clave123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    duplicate_username = {**payload, "email": "otro@example.com"}
    duplicate_email = {**payload, "username": "otro"}
    assert client.post("/api/auth/register", json=duplicate_username).status_code == 400
    assert client.post("/api/auth/register", json=duplicate_email).status_code == 400


def test_register_validates_fields(client):
    assert client.post("/api/auth/register", json={"username": "ab", "email": "no-es-email", "password": "123"}).status_code == 422


def test_login_rejects_unknown_user_and_wrong_password(client, user_factory):
    user_factory()
    unknown = client.post("/api/auth/login/json", json={"username": "fantasma", "password": "secret123"})
    wrong = client.post("/api/auth/login/json", json={"username": "tester", "password": "incorrecta"})
    assert unknown.status_code == wrong.status_code == 401


def test_form_login_endpoint(client, user_factory):
    user_factory()
    success = client.post("/api/auth/login", data={"username": "tester", "password": "secret123"})
    failure = client.post("/api/auth/login", data={"username": "tester", "password": "incorrecta"})
    assert success.status_code == 200
    assert failure.status_code == 401


def test_me_returns_authenticated_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "tester"


def test_invalid_and_expired_tokens_are_rejected(client):
    from datetime import timedelta

    from app.auth import create_access_token

    response = client.get("/api/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401
    expired = create_access_token({"sub": "tester"}, expires_delta=timedelta(seconds=-1))
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_inactive_user_cannot_access_active_user_routes(client, user_factory):
    user = user_factory(is_active=0)
    login = client.post("/api/auth/login/json", json={"username": user.username, "password": "secret123"})
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert response.status_code == 400
