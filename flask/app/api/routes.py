from __future__ import annotations

from flask import Blueprint, jsonify, request, send_file

from app.ml import ensure_artifacts_loaded, get_util

api_bp = Blueprint("api", __name__)


def _payload() -> dict:
    if request.is_json:
        return request.get_json() or {}
    return request.form.to_dict()


@api_bp.before_request
def _load_models():
    ensure_artifacts_loaded()


@api_bp.get("/options")
def get_options():
    return jsonify(get_util().get_options())


@api_bp.post("/predict_rent")
def predict_rent():
    prediction = get_util().predict_rent(_payload())
    return jsonify({"estimated_rent": prediction})


@api_bp.post("/predict_scam")
def predict_scam():
    return jsonify(get_util().predict_scam(_payload()))


@api_bp.post("/verify_text")
def verify_text():
    text = _payload().get("text", "")
    return jsonify(get_util().verify_text(text))


@api_bp.post("/recommend")
def recommend():
    payload = _payload()
    top_n = int(payload.get("top_n", 5))
    items = get_util().recommend_listings(payload, top_n=top_n)
    return jsonify({"recommendations": items})


@api_bp.post("/locality_cluster")
def locality_cluster():
    city = _payload().get("city", "")
    return jsonify(get_util().locality_analysis(city))


@api_bp.post("/inspect_image")
def inspect_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided in request"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No image file selected"}), 400
    try:
        return jsonify(get_util().inspect_image(file.read()))
    except Exception as exc:
        return jsonify({"error": f"Failed to process image: {exc}"}), 500


@api_bp.post("/inspect_video")
def inspect_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided in request"}), 400
    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "No video file selected"}), 400
    try:
        return jsonify(get_util().inspect_video(file.read()))
    except Exception as exc:
        return jsonify({"error": f"Failed to process video: {exc}"}), 500


@api_bp.get("/sample_image/<name>")
def sample_image(name: str):
    path = get_util().get_sample_image_path(name)
    if not path:
        return jsonify({"error": "Sample image not found"}), 404
    mimetype = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return send_file(path, mimetype=mimetype)
