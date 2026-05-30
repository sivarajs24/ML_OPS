# SmartNest Rental Intelligence

A compact, multi-module rental intelligence app for Tamil Nadu rentals using:
- Random Forest Regressor (rent prediction)
- Random Forest + Logistic Regression (fake listing detection)
- Naive Bayes (text verification)
- KNN (recommendations)
- K-Means (locality analysis)

## Quick start

1) Train models and generate artifacts

```powershell
# From d:\smartnest.ai\smartnest_rental_platform
python .\model\train_models.py
```

2) Start the Flask server

```powershell
python .\server\server.py
```

3) Open the UI

Open [smartnest_rental_platform/client/app.html](smartnest_rental_platform/client/app.html) in your browser.

## Smoke test (optional)

```powershell
python .\server\smoke_test.py
```
