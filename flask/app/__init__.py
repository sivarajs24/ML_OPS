from __future__ import annotations

from flask import Flask, jsonify

from app.api.routes import api_bp
from app.config import Config
from app.ml import ensure_artifacts_loaded
from app.web.routes import web_bp


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "smartnest-rental"})

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.route("/api/<path:_path>", methods=["OPTIONS"])
    @app.route("/api", methods=["OPTIONS"])
    def api_options(_path: str = ""):
        return "", 204

    if app.config.get("EAGER_LOAD_ARTIFACTS", True):
        with app.app_context():
            ensure_artifacts_loaded()

    return app
