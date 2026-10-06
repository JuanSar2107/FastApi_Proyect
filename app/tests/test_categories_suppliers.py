def test_category_crud_and_duplicate_validation(client, auth_headers):
    created = client.post("/api/categories", headers=auth_headers, json={"name": "Bebidas", "description": "Frías"})
    assert created.status_code == 201
    category_id = created.json()["id"]
    assert client.get(f"/api/categories/{category_id}", headers=auth_headers).json()["name"] == "Bebidas"
    assert client.get("/api/categories", headers=auth_headers).json()[0]["id"] == category_id
    assert client.post("/api/categories", headers=auth_headers, json={"name": "Bebidas"}).status_code == 400
    updated = client.put(f"/api/categories/{category_id}", headers=auth_headers, json={"description": "Actualizada"})
    assert updated.json()["description"] == "Actualizada"
    assert client.delete(f"/api/categories/{category_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/categories/{category_id}", headers=auth_headers).status_code == 404


def test_category_not_found_and_validation_and_pagination(client, auth_headers):
    assert client.get("/api/categories/999", headers=auth_headers).status_code == 404
    assert client.put("/api/categories/999", headers=auth_headers, json={"name": "x"}).status_code == 404
    assert client.delete("/api/categories/999", headers=auth_headers).status_code == 404
    assert client.post("/api/categories", headers=auth_headers, json={"name": ""}).status_code == 422
    assert client.get("/api/categories?skip=-1", headers=auth_headers).status_code == 422
    assert client.get("/api/categories?limit=0", headers=auth_headers).status_code == 422


def test_supplier_crud_search_and_validation(client, auth_headers):
    payload = {"name": "Acme", "contact_name": "Ana", "email": "ana@acme.com", "phone": "123"}
    created = client.post("/api/suppliers", headers=auth_headers, json=payload)
    assert created.status_code == 201
    supplier_id = created.json()["id"]
    assert len(client.get("/api/suppliers?search=acm", headers=auth_headers).json()) == 1
    assert client.get(f"/api/suppliers/{supplier_id}", headers=auth_headers).json()["email"] == "ana@acme.com"
    assert client.put(f"/api/suppliers/{supplier_id}", headers=auth_headers, json={"phone": "456"}).json()["phone"] == "456"
    assert client.delete(f"/api/suppliers/{supplier_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/suppliers/{supplier_id}", headers=auth_headers).status_code == 404
    assert client.post("/api/suppliers", headers=auth_headers, json={"name": "Proveedor", "email": "invalido"}).status_code == 422


def test_supplier_missing_and_pagination_edges(client, auth_headers):
    assert client.get("/api/suppliers/999", headers=auth_headers).status_code == 404
    assert client.put("/api/suppliers/999", headers=auth_headers, json={"name": "x"}).status_code == 404
    assert client.delete("/api/suppliers/999", headers=auth_headers).status_code == 404
    assert client.get("/api/suppliers?limit=501", headers=auth_headers).status_code == 422
