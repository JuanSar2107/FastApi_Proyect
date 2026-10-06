def test_user_routes_require_admin(client, auth_headers):
    assert client.get("/api/users", headers=auth_headers).status_code == 403
    assert client.post("/api/users", headers=auth_headers, json={"username": "nuevo", "email": "nuevo@example.com", "password": "clave123"}).status_code == 403


def test_admin_user_crud_duplicate_checks_and_self_delete_protection(client, admin_headers):
    payload = {"username": "persona", "email": "persona@example.com", "password": "clave123", "full_name": "Persona"}
    created = client.post("/api/users", headers=admin_headers, json=payload)
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert client.get("/api/users", headers=admin_headers).status_code == 200
    assert client.get(f"/api/users/{user_id}", headers=admin_headers).json()["username"] == "persona"
    assert client.post("/api/users", headers=admin_headers, json={**payload, "email": "otro@example.com"}).status_code == 400
    assert client.post("/api/users", headers=admin_headers, json={**payload, "username": "otro"}).status_code == 400
    updated = client.put(f"/api/users/{user_id}", headers=admin_headers, json={"full_name": "Nombre actualizado"})
    assert updated.json()["full_name"] == "Nombre actualizado"
    assert client.delete(f"/api/users/{user_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/users/{user_id}", headers=admin_headers).status_code == 404
    assert client.delete("/api/users/1", headers=admin_headers).status_code == 400


def test_admin_user_missing_and_validation(client, admin_headers):
    assert client.get("/api/users/999", headers=admin_headers).status_code == 404
    assert client.put("/api/users/999", headers=admin_headers, json={"role": "user"}).status_code == 404
    assert client.delete("/api/users/999", headers=admin_headers).status_code == 404
    invalid = {"username": "ab", "email": "correo-invalido", "password": "1"}
    assert client.post("/api/users", headers=admin_headers, json=invalid).status_code == 422
    assert client.get("/api/users?limit=0", headers=admin_headers).status_code == 422


def test_low_stock_report_and_summary(client, auth_headers, catalog_factory, db_session):
    catalog_factory(stock=1, min_stock=5)
    low_stock = client.get("/api/reports/low-stock", headers=auth_headers)
    assert low_stock.status_code == 200
    assert low_stock.json()[0]["shortage"] == 4
    summary = client.get("/api/reports/summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json() == {
        "total_products": 1,
        "total_categories": 1,
        "total_suppliers": 1,
        "total_stock_value": 7.25,
        "low_stock_count": 1,
        "recent_movements": 0,
    }


def test_reports_exclude_inactive_products(client, auth_headers, catalog_factory):
    catalog_factory(stock=0, min_stock=3, active=0)
    assert client.get("/api/reports/low-stock", headers=auth_headers).json() == []
    assert client.get("/api/reports/summary", headers=auth_headers).json()["total_products"] == 0
