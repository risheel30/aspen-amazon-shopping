from datetime import datetime

from flask import Blueprint, jsonify, request

from shopapi.auth import require_api_key
from shopapi.db import get_session
from shopapi.models.image import ProductImage
from shopapi.models.product import Product
from shopapi.models.spec import ProductSpec
from shopapi.models.variant import ProductVariant
from shopapi.services.scraper_service import fetch_product


bp = Blueprint("products", __name__, url_prefix="/products")


def _save_product(data, session, existing=None):
    if existing is None:
        product = Product(url=data["url"])
        session.add(product)
    else:
        product = existing
        product.images.clear()
        product.specs.clear()
        product.variants.clear()

    product.asin = data.get("asin")
    product.url = data.get("url") or product.url
    product.title = data.get("title")
    product.brand = data.get("brand")
    product.seller = data.get("seller")
    product.availability = data.get("availability")
    product.price_amount = data.get("price_amount")
    product.price_currency = data.get("price_currency")
    product.list_price_amount = data.get("list_price_amount")
    product.rating = data.get("rating")
    product.review_count = data.get("review_count")
    product.description = data.get("description")
    product.feature_bullets = data.get("feature_bullets") or []
    product.fetched_at = datetime.utcnow()

    for img in data.get("images", []):
        product.images.append(
            ProductImage(url=img["url"], position=img.get("position", 0), is_main=img.get("is_main", False))
        )
    for s in data.get("specs", []):
        product.specs.append(ProductSpec(key=s["key"], value=s.get("value")))
    for v in data.get("variants", []):
        product.variants.append(ProductVariant(kind=v["kind"], value=v["value"], asin=v.get("asin")))

    session.flush()
    return product


@bp.post("")
@require_api_key
def create_product():
    body = request.get_json(silent=True) or {}
    url = body.get("url")
    if not url:
        return jsonify({"error": "url is required"}), 400

    data = fetch_product(url)

    session = get_session()
    try:
        product = _save_product(data, session)
        session.commit()
        return jsonify(product.to_dict(deep=True)), 201
    finally:
        session.close()


@bp.get("")
@require_api_key
def list_products():
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    session = get_session()
    try:
        rows = session.query(Product).order_by(Product.id.desc()).offset(offset).limit(limit).all()
        return jsonify([p.to_dict() for p in rows]), 200
    finally:
        session.close()


@bp.get("/<int:pid>")
@require_api_key
def get_product(pid):
    session = get_session()
    try:
        product = session.get(Product, pid)
        if not product:
            return jsonify({"error": "not found"}), 404
        return jsonify(product.to_dict(deep=True)), 200
    finally:
        session.close()


@bp.put("/<int:pid>")
@require_api_key
def update_product(pid):
    body = request.get_json(silent=True) or {}
    editable = {"title", "price_amount", "price_currency", "availability", "description", "brand", "seller"}
    session = get_session()
    try:
        product = session.get(Product, pid)
        if not product:
            return jsonify({"error": "not found"}), 404
        for key, value in body.items():
            if key in editable:
                setattr(product, key, value)
        session.commit()
        return jsonify(product.to_dict(deep=True)), 200
    finally:
        session.close()


@bp.delete("/<int:pid>")
@require_api_key
def delete_product(pid):
    session = get_session()
    try:
        product = session.get(Product, pid)
        if not product:
            return jsonify({"error": "not found"}), 404
        session.delete(product)
        session.commit()
        return jsonify({"deleted": pid}), 200
    finally:
        session.close()


@bp.post("/<int:pid>/refresh")
@require_api_key
def refresh_product(pid):
    session = get_session()
    try:
        product = session.get(Product, pid)
        if not product:
            return jsonify({"error": "not found"}), 404
        data = fetch_product(product.url)
        product = _save_product(data, session, existing=product)
        session.commit()
        return jsonify(product.to_dict(deep=True)), 200
    finally:
        session.close()
