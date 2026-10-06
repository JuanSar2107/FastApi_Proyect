def test_product_crud_search_filters_and_soft_delete(client, auth_headers, catalog_factory):
    category, supplier, product = catalog_factory()
    listed = client.get("/api/products", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["category"]["id"] == category.id
    assert listed.json()[0]["supplier"]["id"] == supplier.id
    assert len(client.get("/api/products?search=sku-test", headers=auth_headers).json()) == 1
    assert len(client.get(f"/api/products?category_id={category.id}", headers=auth_headers).json()) == 1
    assert len(client.get(f"/api/products?supplier_id={supplier.id}", headers=auth_headers).json()) == 1
    assert len(client.get("/api/products?low_stock=true", headers=auth_headers).json()) == 0
    assert client.get(f"/api/products/{product.id}", headers=auth_headers).json()["sku"] == "SKU-TEST"
    assert client.put(f"/api/products/{product.id}", headers=auth_headers, json={"price": 20}).json()["price"] == 20
    assert client.delete(f"/api/products/{product.id}", headers=auth_headers).status_code == 204
    assert client.get("/api/products", headers=auth_headers).json() == []
    assert client.get(f"/api/products/{product.id}", headers=auth_headers).status_code == 200


def test_product_creation_duplicate_validation_and_not_found(client, auth_headers):
    payload = {"name": "Producto", "sku": "DUP-1", "price": 5, "stock_quantity": 4}
    assert client.post("/api/products", headers=auth_headers, json=payload).status_code == 201
    duplicate = client.post("/api/products", headers=auth_headers, json=payload)
    assert duplicate.status_code == 400
    assert client.post("/api/products", headers=auth_headers, json={**payload, "sku": "DUP-2", "price": -1}).status_code == 422
    assert client.get("/api/products/999", headers=auth_headers).status_code == 404
    assert client.put("/api/products/999", headers=auth_headers, json={"name": "x"}).status_code == 404
    assert client.delete("/api/products/999", headers=auth_headers).status_code == 404
    assert client.get("/api/products?skip=-1", headers=auth_headers).status_code == 422


def test_inventory_entry_exit_and_adjustment_update_stock(client, auth_headers, catalog_factory):
    _, _, product = catalog_factory(stock=10)
    entry = client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": product.id, "movement_type": "entry", "quantity": 5})
    assert entry.status_code == 201
    assert (entry.json()["previous_stock"], entry.json()["new_stock"]) == (10, 15)
    exit_response = client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": product.id, "movement_type": "exit", "quantity": 3})
    assert (exit_response.json()["previous_stock"], exit_response.json()["new_stock"]) == (15, 12)
    adjustment = client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": product.id, "movement_type": "adjustment", "quantity": 4})
    assert adjustment.json()["new_stock"] == 4
    assert client.get(f"/api/products/{product.id}", headers=auth_headers).json()["stock_quantity"] == 4


def test_inventory_rejects_invalid_movements_and_insufficient_stock(client, auth_headers, catalog_factory):
    _, _, product = catalog_factory(stock=2)
    base = {"product_id": product.id, "quantity": 1}
    assert client.post("/api/inventory/movements", headers=auth_headers, json={**base, "movement_type": "exit", "quantity": 3}).status_code == 400
    assert client.post("/api/inventory/movements", headers=auth_headers, json={**base, "movement_type": "adjustment", "quantity": -1}).status_code == 422
    assert client.post("/api/inventory/movements", headers=auth_headers, json={**base, "movement_type": "invalid"}).status_code == 422
    assert client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": 999, "movement_type": "entry", "quantity": 1}).status_code == 404
    assert client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": product.id, "movement_type": "entry", "quantity": 0}).status_code == 422


def test_inventory_movement_list_filters_get_and_not_found(client, auth_headers, catalog_factory):
    _, _, product = catalog_factory()
    for kind in ("entry", "exit"):
        client.post("/api/inventory/movements", headers=auth_headers, json={"product_id": product.id, "movement_type": kind, "quantity": 1})
    all_movements = client.get("/api/inventory/movements", headers=auth_headers).json()
    assert len(all_movements) == 2
    movement_id = all_movements[0]["id"]
    assert client.get(f"/api/inventory/movements/{movement_id}", headers=auth_headers).status_code == 200
    assert len(client.get(f"/api/inventory/movements?product_id={product.id}&movement_type=entry", headers=auth_headers).json()) == 1
    assert client.get("/api/inventory/movements/999", headers=auth_headers).status_code == 404
    assert client.get("/api/inventory/movements?limit=0", headers=auth_headers).status_code == 422
