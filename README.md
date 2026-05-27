# amazon-shopping

Small Flask backend that takes an Amazon product link, scrapes the product page, and stores everything in SQLite. Used as Aspen substrate for a rate-limit handling task.

## What it does

Send an Amazon product URL to `POST /products` and the backend fetches the page, parses out title, price, rating, review count, images, feature bullets, description, brand, seller, availability, specs, and variants. Then it stores it all in SQLite via SQLAlchemy.

## Endpoints

All endpoints need `X-API-Key` header. Default key in dev is `dev-key-risheel`. Override with `SHOP_API_KEY` env var.

| Method | Path | What |
|---|---|---|
| GET | / | health |
| POST | /products | body `{"url": "..."}`. Scrapes and saves. Returns full product. |
| GET | /products | list products, supports `?limit=`, `?offset=` |
| GET | /products/<id> | get one product with images, specs, variants |
| PUT | /products/<id> | edit title, price_amount, price_currency, availability, description, brand, seller |
| DELETE | /products/<id> | delete product and its children |
| POST | /products/<id>/refresh | re-scrape using stored URL |

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m shopapi.main
```

Then in another shell:

```bash
curl -s -X POST http://127.0.0.1:5000/products \
  -H "X-API-Key: dev-key-risheel" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B09XS7JWHH"}' | python3 -m json.tool
```

## Tests

```bash
.venv/bin/pytest -v
```

The smoke tests patch `requests.get` so no real Amazon traffic happens during tests.

## Storage layout

- `products` row per scraped product (asin, url, title, price, rating, ...)
- `product_images` child rows with image URLs
- `product_specs` child rows for the spec table
- `product_variants` child rows for size/color options

## What is missing (on purpose)

The scraper does not handle Amazon rate-limit or block responses. When Amazon throttles, the scraper still parses whatever HTML came back and saves it. This is the scenario the Aspen agent has to write tests for.
