from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

import joblib
import numpy as np
import pandas as pd

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

rent_model = None
rent_columns: List[str] = []

scam_lr_model = None
scam_rf_model = None
scam_columns: List[str] = []

text_nb_model = None
text_vectorizer = None

reco_preprocessor = None
reco_nn_model = None
reco_matrix = None
listing_summary: pd.DataFrame | None = None

locality_kmeans = None
locality_scaler = None
locality_city_stats: pd.DataFrame | None = None

options: Dict[str, List[str]] = {}

CAT_COLS = ["City", "Area Type", "Furnishing Status", "Tenant Preferred"]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_saved_artifacts() -> None:
    global rent_model, rent_columns
    global scam_lr_model, scam_rf_model, scam_columns
    global text_nb_model, text_vectorizer
    global reco_preprocessor, reco_nn_model, reco_matrix, listing_summary
    global locality_kmeans, locality_scaler, locality_city_stats
    global options

    rent_model = joblib.load(ARTIFACT_DIR / "rent_model.pkl")
    rent_columns = _load_json(ARTIFACT_DIR / "rent_columns.json")["columns"]

    scam_lr_model = joblib.load(ARTIFACT_DIR / "scam_lr_model.pkl")
    scam_rf_model = joblib.load(ARTIFACT_DIR / "scam_rf_model.pkl")
    scam_columns = _load_json(ARTIFACT_DIR / "scam_columns.json")["columns"]

    # Compatibility shim: some models were serialized with newer scikit-learn
    # which may include attributes not present in older runtime versions.
    # Ensure minimal attributes expected by predict_proba exist.
    try:
        if scam_lr_model is not None and not hasattr(scam_lr_model, "multi_class"):
            scam_lr_model.multi_class = "ovr"
    except Exception:
        pass

    text_nb_model = joblib.load(ARTIFACT_DIR / "text_nb_model.pkl")
    text_vectorizer = joblib.load(ARTIFACT_DIR / "text_vectorizer.pkl")

    reco_preprocessor = joblib.load(ARTIFACT_DIR / "reco_preprocessor.pkl")
    reco_nn_model = joblib.load(ARTIFACT_DIR / "reco_nn_model.pkl")
    reco_matrix = joblib.load(ARTIFACT_DIR / "reco_matrix.pkl")
    listing_summary = pd.read_csv(ARTIFACT_DIR / "listing_summary.csv")

    locality_kmeans = joblib.load(ARTIFACT_DIR / "locality_kmeans.pkl")
    locality_scaler = joblib.load(ARTIFACT_DIR / "locality_scaler.pkl")
    locality_city_stats = pd.read_csv(ARTIFACT_DIR / "locality_city_stats.csv")

    options = _load_json(ARTIFACT_DIR / "options.json")


def get_options() -> Dict[str, List[str]]:
    return options


def _build_feature_frame(payload: Dict[str, Any], columns: List[str]) -> pd.DataFrame:
    row = {
        "Size": float(payload.get("size", 0)),
        "BHK": int(payload.get("bhk", 0)),
        "Bathroom": int(payload.get("bathroom", 0)),
        "Rent": float(payload.get("rent", 0)),
        "City": payload.get("city", ""),
        "Area Type": payload.get("area_type", ""),
        "Furnishing Status": payload.get("furnishing_status", ""),
        "Tenant Preferred": payload.get("tenant_preferred", ""),
    }

    df = pd.DataFrame([row])
    df = pd.get_dummies(df, columns=CAT_COLS)

    for col in columns:
        if col not in df.columns:
            df[col] = 0

    df = df[columns]
    return df


def predict_rent(payload: Dict[str, Any]) -> float:
    df = _build_feature_frame(payload, rent_columns)
    prediction = rent_model.predict(df)[0]
    return round(float(prediction), 2)


def predict_scam(payload: Dict[str, Any]) -> Dict[str, Any]:
    df = _build_feature_frame(payload, scam_columns)

    lr_prob = float(scam_lr_model.predict_proba(df)[0][1])
    rf_prob = float(scam_rf_model.predict_proba(df)[0][1])

    label = "yes" if max(lr_prob, rf_prob) >= 0.5 else "no"

    return {
        "label": label,
        "logistic_probability": round(lr_prob, 4),
        "random_forest_probability": round(rf_prob, 4),
    }


def verify_text(text: str) -> Dict[str, Any]:
    text = text or ""
    vec = text_vectorizer.transform([text])
    prob = float(text_nb_model.predict_proba(vec)[0][1])
    label = "yes" if prob >= 0.5 else "no"
    return {"label": label, "probability": round(prob, 4)}


def recommend_listings(payload: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
    if listing_summary is None:
        return []

    row = pd.DataFrame([
        {
            "Size": float(payload.get("size", 0)),
            "BHK": int(payload.get("bhk", 0)),
            "Bathroom": int(payload.get("bathroom", 0)),
            "Rent": float(payload.get("rent", 0)),
            "City": payload.get("city", ""),
            "Area Type": payload.get("area_type", ""),
            "Furnishing Status": payload.get("furnishing_status", ""),
            "Tenant Preferred": payload.get("tenant_preferred", ""),
        }
    ])

    X_input = reco_preprocessor.transform(row)
    n_neighbors = min(top_n + 1, len(listing_summary))
    distances, indices = reco_nn_model.kneighbors(X_input, n_neighbors=n_neighbors)

    results = []
    for idx in indices[0][1:]:
        listing = listing_summary.iloc[idx].to_dict()
        results.append(listing)

    return results


def locality_analysis(city: str) -> Dict[str, Any]:
    if locality_city_stats is None:
        return {"error": "Locality stats not loaded"}

    stats = locality_city_stats[locality_city_stats["City"] == city]
    if stats.empty:
        return {"error": "City not found"}

    row = stats.iloc[0]
    cluster_id = int(row["cluster"])

    same_cluster = locality_city_stats[locality_city_stats["cluster"] == cluster_id]
    top_cities = same_cluster.sort_values("avg_rent", ascending=False).head(5)["City"].tolist()

    return {
        "city": city,
        "cluster": cluster_id,
        "avg_rent": round(float(row["avg_rent"]), 2),
        "avg_size": round(float(row["avg_size"]), 2),
        "avg_bhk": round(float(row["avg_bhk"]), 2),
        "avg_bath": round(float(row["avg_bath"]), 2),
        "listings": int(row["listings"]),
        "similar_cities": top_cities,
    }
