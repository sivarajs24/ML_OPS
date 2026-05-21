# SVM - Tenant Preference Classification

Dataset:
`../House_Rent_Dataset_TN_synthetic_text_1500_preprocessed.csv`

Notebook:
`house_rent_svm_tenant_preference.ipynb`

Problem:
Predict tenant preference for a rental listing.

Target:
`Tenant Preferred`

Target classes:
`bachelors`, `family`, `bachelors/family`

Features:
`Rent`, `BHK`, `Size`, `Bathroom`, `Area Type`, `Furnishing Status`, `Point of Contact`

Algorithm:
`SVC`

Notebook work:
- Load dataset
- Select features and target
- Convert categorical columns using `pd.get_dummies`
- Split train and test data
- Train SVM model
- Check score, confusion matrix and classification report
- Predict first 5 test records
- Save model

Output:
`house_rent_svm_tenant_preference.pkl`
