PRODUCT_URL = "https://www.amazon.com/dp/B09XS7JWHH"


def test_root_works(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_create_requires_auth(client):
    r = client.post("/products", json={"url": PRODUCT_URL})
    assert r.status_code == 401


def test_create_rejects_wrong_key(client, auth_invalid):
    r = client.post("/products", headers=auth_invalid, json={"url": PRODUCT_URL})
    assert r.status_code == 401


def test_create_requires_url(client, auth_valid, fake_amazon_ok):
    r = client.post("/products", headers=auth_valid, json={})
    assert r.status_code == 400


def test_create_product_ok(client, auth_valid, fake_amazon_ok):
    r = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    assert r.status_code == 201
    body = r.get_json()
    assert body["title"] == "Sony WH-1000XM5 Headphones"
    assert body["price_amount"] == 348.0
    assert body["price_currency"] == "USD"
    assert body["asin"] == "B09XS7JWHH"
    assert body["rating"] == 4.6
    assert body["review_count"] == 12345
    assert len(body["feature_bullets"]) == 2
    assert len(body["images"]) >= 1


def test_list_products_empty(client, auth_valid):
    r = client.get("/products", headers=auth_valid)
    assert r.status_code == 200
    assert r.get_json() == []


def test_list_products_after_create(client, auth_valid, fake_amazon_ok):
    client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    r = client.get("/products", headers=auth_valid)
    assert r.status_code == 200
    rows = r.get_json()
    assert len(rows) == 1
    assert rows[0]["asin"] == "B09XS7JWHH"


def test_get_product_by_id(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.get(f"/products/{pid}", headers=auth_valid)
    assert r.status_code == 200
    body = r.get_json()
    assert body["id"] == pid
    assert "images" in body and "specs" in body and "variants" in body


def test_get_product_unknown_returns_404(client, auth_valid):
    r = client.get("/products/9999", headers=auth_valid)
    assert r.status_code == 404


def test_update_product_title(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.put(f"/products/{pid}", headers=auth_valid, json={"title": "Custom Title"})
    assert r.status_code == 200
    assert r.get_json()["title"] == "Custom Title"


def test_update_ignores_unknown_fields(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.put(f"/products/{pid}", headers=auth_valid, json={"rating": 1.0})
    assert r.status_code == 200
    assert r.get_json()["rating"] == 4.6


def test_delete_product(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.delete(f"/products/{pid}", headers=auth_valid)
    assert r.status_code == 200
    g = client.get(f"/products/{pid}", headers=auth_valid)
    assert g.status_code == 404


def test_delete_unknown_returns_404(client, auth_valid):
    r = client.delete("/products/9999", headers=auth_valid)
    assert r.status_code == 404


def test_refresh_re_scrapes(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.post(f"/products/{pid}/refresh", headers=auth_valid)
    assert r.status_code == 200
    assert r.get_json()["asin"] == "B09XS7JWHH"


def test_product_has_specs_and_variants(client, auth_valid, fake_amazon_ok):
    c = client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    pid = c.get_json()["id"]
    r = client.get(f"/products/{pid}", headers=auth_valid)
    body = r.get_json()
    spec_keys = {s["key"] for s in body["specs"]}
    assert "Color" in spec_keys
    variant_values = {v["value"] for v in body["variants"]}
    assert "Black" in variant_values


def test_list_pagination_limit(client, auth_valid, fake_amazon_ok):
    for _ in range(3):
        client.post("/products", headers=auth_valid, json={"url": PRODUCT_URL})
    r = client.get("/products?limit=2", headers=auth_valid)
    assert r.status_code == 200
    assert len(r.get_json()) == 2
