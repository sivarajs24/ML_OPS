from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "smartnest_rental_platform" / "model" / "House_Rent_Dataset_TN_synthetic_text_1500_preprocessed.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

NUM_COLS = ["Size", "BHK", "Bathroom", "Rent"]
CAT_COLS = ["City", "Area Type", "Furnishing Status", "Tenant Preferred"]

TEXT_COLS = [
    "Listing_Title",
    "Listing_Description",
    "Amenities_Text",
    "Landmarks_Text",
    "Reviews_Text",
    "Complaints_Text",
    "Lease_Rules_Text",
    "Inquiry_Text",
    "Inspection_Notes_Text",
]


def _load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    for col in NUM_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Size", "BHK", "Bathroom", "Rent"])
    df["Scam_Flag"] = df["Scam_Flag"].astype(str).str.lower().map({"yes": 1, "no": 0})
    df["Scam_Flag"] = df["Scam_Flag"].fillna(0).astype(int)
    return df


def _save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2))


def train_rent_model(df: pd.DataFrame) -> None:
    features = ["Size", "BHK", "Bathroom", "City", "Area Type", "Furnishing Status", "Tenant Preferred"]
    target = "Rent"

    X = df[features].copy()
    y = df[target].copy()

    X_dummies = pd.get_dummies(X, columns=["City", "Area Type", "Furnishing Status", "Tenant Preferred"])

    X_train, X_test, y_train, y_test = train_test_split(
        X_dummies, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300, random_state=42, n_jobs=-1, max_depth=None
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    print(f"[Rent RF] MAE={mae:.2f} RMSE={rmse:.2f} R2={r2:.3f}")

    joblib.dump(model, ARTIFACT_DIR / "rent_model.pkl")
    _save_json(ARTIFACT_DIR / "rent_columns.json", {"columns": X_dummies.columns.tolist()})


def train_scam_models(df: pd.DataFrame) -> None:
    features = [
        "Rent",
        "Size",
        "BHK",
        "Bathroom",
        "City",
        "Area Type",
        "Furnishing Status",
        "Tenant Preferred",
    ]
    X = df[features].copy()
    y = df["Scam_Flag"].copy()

    X_dummies = pd.get_dummies(X, columns=["City", "Area Type", "Furnishing Status", "Tenant Preferred"])

    X_train, X_test, y_train, y_test = train_test_split(
        X_dummies, y, test_size=0.2, random_state=42, stratify=y
    )

    lr_model = LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")
    lr_model.fit(X_train, y_train)

    rf_model = RandomForestClassifier(
        n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced"
    )
    rf_model.fit(X_train, y_train)

    lr_score = lr_model.score(X_test, y_test)
    rf_score = rf_model.score(X_test, y_test)
    print(f"[Scam LR] Accuracy={lr_score:.3f} | [Scam RF] Accuracy={rf_score:.3f}")

    joblib.dump(lr_model, ARTIFACT_DIR / "scam_lr_model.pkl")
    joblib.dump(rf_model, ARTIFACT_DIR / "scam_rf_model.pkl")
    _save_json(ARTIFACT_DIR / "scam_columns.json", {"columns": X_dummies.columns.tolist()})


def train_text_verification(df: pd.DataFrame) -> None:
    df = df.copy()
    df["text_all"] = df[TEXT_COLS].fillna("").agg(" ".join, axis=1)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text_all"], df["Scam_Flag"], test_size=0.2, random_state=42, stratify=df["Scam_Flag"]
    )

    vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words="english")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = MultinomialNB()
    model.fit(X_train_vec, y_train)
    score = model.score(X_test_vec, y_test)
    print(f"[Text NB] Accuracy={score:.3f}")

    joblib.dump(model, ARTIFACT_DIR / "text_nb_model.pkl")
    joblib.dump(vectorizer, ARTIFACT_DIR / "text_vectorizer.pkl")


def train_recommendation(df: pd.DataFrame) -> None:
    features = ["Size", "BHK", "Bathroom", "Rent", "City", "Area Type", "Furnishing Status", "Tenant Preferred"]
    X = df[features].copy()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), ["Size", "BHK", "Bathroom", "Rent"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["City", "Area Type", "Furnishing Status", "Tenant Preferred"]),
        ]
    )

    X_processed = preprocessor.fit_transform(X)
    nn_model = NearestNeighbors(metric="cosine", n_neighbors=6)
    nn_model.fit(X_processed)

    summary_cols = [
        "City",
        "Area Locality",
        "Rent",
        "Size",
        "BHK",
        "Bathroom",
        "Furnishing Status",
        "Tenant Preferred",
    ]
    df[summary_cols].to_csv(ARTIFACT_DIR / "listing_summary.csv", index=False)

    joblib.dump(preprocessor, ARTIFACT_DIR / "reco_preprocessor.pkl")
    joblib.dump(nn_model, ARTIFACT_DIR / "reco_nn_model.pkl")
    joblib.dump(X_processed, ARTIFACT_DIR / "reco_matrix.pkl")


def train_locality(df: pd.DataFrame) -> None:
    city_stats = (
        df.groupby("City")
        .agg(
            avg_rent=("Rent", "mean"),
            avg_size=("Size", "mean"),
            avg_bhk=("BHK", "mean"),
            avg_bath=("Bathroom", "mean"),
            listings=("Rent", "count"),
        )
        .reset_index()
    )

    features = city_stats[["avg_rent", "avg_size", "avg_bhk", "avg_bath"]]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    n_clusters = max(1, min(4, len(city_stats)))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    city_stats["cluster"] = kmeans.fit_predict(scaled)

    joblib.dump(kmeans, ARTIFACT_DIR / "locality_kmeans.pkl")
    joblib.dump(scaler, ARTIFACT_DIR / "locality_scaler.pkl")
    city_stats.to_csv(ARTIFACT_DIR / "locality_city_stats.csv", index=False)


def save_options(df: pd.DataFrame) -> None:
    payload = {
        "cities": sorted(df["City"].dropna().unique().tolist()),
        "area_types": sorted(df["Area Type"].dropna().unique().tolist()),
        "furnishing_statuses": sorted(df["Furnishing Status"].dropna().unique().tolist()),
        "tenant_preferred": sorted(df["Tenant Preferred"].dropna().unique().tolist()),
    }
    _save_json(ARTIFACT_DIR / "options.json", payload)


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    df = _load_data()

    save_options(df)
    train_rent_model(df)
    train_scam_models(df)
    train_text_verification(df)
    train_recommendation(df)
    train_locality(df)

    print("Artifacts saved in:", ARTIFACT_DIR)


if __name__ == "__main__":
    main()
