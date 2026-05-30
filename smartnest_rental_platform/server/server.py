from __future__ import annotations

from flask import Flask, request, jsonify
import util

app = Flask(__name__)


def _payload() -> dict:
    if request.is_json:
        return request.get_json() or {}
    return request.form.to_dict()


@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


@app.route("/api/options", methods=["GET"])
def get_options():
    return jsonify(util.get_options())


@app.route("/api/predict_rent", methods=["POST"])
def predict_rent():
    payload = _payload()
    prediction = util.predict_rent(payload)
    return jsonify({"estimated_rent": prediction})


@app.route("/api/predict_scam", methods=["POST"])
def predict_scam():
    payload = _payload()
    result = util.predict_scam(payload)
    return jsonify(result)


@app.route("/api/verify_text", methods=["POST"])
def verify_text():
    payload = _payload()
    text = payload.get("text", "")
    result = util.verify_text(text)
    return jsonify(result)


@app.route("/api/recommend", methods=["POST"])
def recommend():
    payload = _payload()
    top_n = int(payload.get("top_n", 5))
    recommendations = util.recommend_listings(payload, top_n=top_n)
    return jsonify({"recommendations": recommendations})


@app.route("/api/locality_cluster", methods=["POST"])
def locality_cluster():
    payload = _payload()
    city = payload.get("city", "")
    result = util.locality_analysis(city)
    return jsonify(result)


if __name__ == "__main__":
    print("Starting SmartNest Flask server...")
    util.load_saved_artifacts()
    app.run()
