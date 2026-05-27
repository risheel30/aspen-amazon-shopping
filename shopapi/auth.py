import os
from functools import wraps

from flask import jsonify, request


def get_expected_key():
    return os.environ.get("SHOP_API_KEY", "dev-key-risheel")


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        sent = request.headers.get("X-API-Key", "")
        if sent != get_expected_key():
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper
