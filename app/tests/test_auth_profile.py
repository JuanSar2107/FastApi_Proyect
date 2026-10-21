def _login(client, username, password):
    return client.post("/api/auth/login/json", json={"username": username, "password": password})


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


# --- Registro: no se puede escalar privilegios ---

def test_register_ignores_role_admin(client):
    payload = {"username": "intruso", "email": "intruso@example.com", "password": "clave123", "role": "admin"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["role"] == "user"

    token = _login(client, "intruso", "clave123").json()["access_token"]
    assert client.get("/api/auth/me", headers=_bearer(token)).json()["role"] == "user"
    assert client.get("/api/users", headers=_bearer(token)).status_code == 403


def test_admin_can_still_assign_role(client, admin_headers):
    payload = {"username": "jefe", "email": "jefe@example.com", "password": "clave123", "role": "admin"}
    response = client.post("/api/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


# --- Cambio de contraseña ---

def test_change_password_requires_auth(client):
    body = {"current_password": "secret123", "new_password": "nueva-clave-1"}
    assert client.post("/api/auth/change-password", json=body).status_code == 401


def test_change_password_rejects_wrong_current_password(client, auth_headers):
    body = {"current_password": "incorrecta", "new_password": "nueva-clave-1"}
    response = client.post("/api/auth/change-password", json=body, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "La contraseña actual no es correcta"


def test_change_password_rejects_same_password(client, auth_headers):
    body = {"current_password": "secret123", "new_password": "secret123"}
    response = client.post("/api/auth/change-password", json=body, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "La nueva contraseña debe ser distinta de la actual"


def test_change_password_validates_min_length(client, auth_headers):
    body = {"current_password": "secret123", "new_password": "corta"}
    assert client.post("/api/auth/change-password", json=body, headers=auth_headers).status_code == 422


def test_change_password_success_updates_login(client, auth_headers):
    body = {"current_password": "secret123", "new_password": "nueva-clave-1"}
    response = client.post("/api/auth/change-password", json=body, headers=auth_headers)
    assert response.status_code == 204
    assert response.content == b""

    assert _login(client, "tester", "nueva-clave-1").status_code == 200
    assert _login(client, "tester", "secret123").status_code == 401


# --- Edición del perfil propio ---

def test_update_me_requires_auth(client):
    assert client.put("/api/auth/me", json={"full_name": "X"}).status_code == 401


def test_update_me_changes_email_and_full_name(client, auth_headers):
    body = {"email": "nuevo-correo@example.com", "full_name": "Nombre Nuevo"}
    response = client.put("/api/auth/me", json=body, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "nuevo-correo@example.com"
    assert data["user"]["full_name"] == "Nombre Nuevo"
    assert data["user"]["username"] == "tester"
    assert "hashed_password" not in data["user"]


def test_update_me_full_name_can_be_cleared(client, auth_headers):
    response = client.put("/api/auth/me", json={"full_name": None}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["user"]["full_name"] is None


def test_update_me_changes_username_and_returns_new_token(client, auth_headers):
    response = client.put("/api/auth/me", json={"username": "renombrado"}, headers=auth_headers)
    assert response.status_code == 200
    new_token = response.json()["access_token"]
    assert response.json()["user"]["username"] == "renombrado"

    me = client.get("/api/auth/me", headers=_bearer(new_token))
    assert me.status_code == 200
    assert me.json()["username"] == "renombrado"
    # El token anterior apuntaba al username viejo y ya no es válido.
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 401
    assert _login(client, "renombrado", "secret123").status_code == 200


def test_update_me_keeping_own_username_and_email_is_allowed(client, auth_headers):
    body = {"username": "tester", "email": "tester@example.com"}
    assert client.put("/api/auth/me", json=body, headers=auth_headers).status_code == 200


def test_update_me_rejects_duplicate_username_and_email(client, auth_headers, user_factory):
    user_factory(username="ocupado", email="ocupado@example.com")

    dup_user = client.put("/api/auth/me", json={"username": "ocupado"}, headers=auth_headers)
    assert dup_user.status_code == 409
    assert dup_user.json()["detail"] == "El nombre de usuario ya existe"

    dup_email = client.put("/api/auth/me", json={"email": "ocupado@example.com"}, headers=auth_headers)
    assert dup_email.status_code == 409
    assert dup_email.json()["detail"] == "El email ya está registrado"


def test_update_me_cannot_change_role_or_is_active(client, auth_headers):
    body = {"full_name": "Quiero ser admin", "role": "admin", "is_active": 0}
    response = client.put("/api/auth/me", json=body, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"
    assert response.json()["user"]["is_active"] == 1

    me = client.get("/api/auth/me", headers=_bearer(response.json()["access_token"]))
    assert me.json()["role"] == "user"
    assert client.get("/api/users", headers=_bearer(response.json()["access_token"])).status_code == 403


def test_update_me_validates_fields(client, auth_headers):
    assert client.put("/api/auth/me", json={"username": "ab"}, headers=auth_headers).status_code == 422
    assert client.put("/api/auth/me", json={"email": "no-es-email"}, headers=auth_headers).status_code == 422
    assert client.put("/api/auth/me", json={"username": None}, headers=auth_headers).status_code == 422
