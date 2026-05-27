from flask import Flask, jsonify

from shopapi.api.products import bp as products_bp
from shopapi.db import init_db


def create_app():
    app = Flask(__name__)

    init_db()

    app.register_blueprint(products_bp)

    @app.get("/")
    def root():
        return jsonify({"app": "amazon-shopping", "status": "ok"}), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
