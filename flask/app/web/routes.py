from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, current_app, send_from_directory

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    client_dir = Path(current_app.config["CLIENT_DIR"])
    return send_from_directory(client_dir, "app.html")


@web_bp.get("/<path:filename>")
def client_assets(filename: str):
    if filename.startswith("api"):
        abort(404)

    client_dir = Path(current_app.config["CLIENT_DIR"])
    target = client_dir / filename
    if not target.is_file():
        abort(404)
    return send_from_directory(client_dir, filename)
