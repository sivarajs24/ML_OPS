# Multiclass Logistic Regression - Rent Tier Classification

Dataset:
`../House_Rent_Dataset_TN_synthetic_text_1500_preprocessed.csv`

Notebook:
`house_rent_multiclass_logistic_rent_tier.ipynb`

Problem:
Predict the rent category of a rental house.

Target:
`Rent_Category`

Target classes:
`Budget`, `Standard`, `Premium`, `Luxury`

Features:
`BHK`, `Size`, `Bathroom`, `Area Type`, `Furnishing Status`, `Tenant Preferred`, `Point of Contact`

Algorithm:
`LogisticRegression`

Notebook work:
- Load dataset
- Create rent categories from `Rent`
- Select features and target
- Convert categorical columns using `pd.get_dummies`
- Split train and test data
- Train logistic regression model
- Check score, confusion matrix and classification report
- Plot confusion matrix heatmap
- Predict first 5 test records
- Save model

Output:
`house_rent_multiclass_logistic_rent_tier.pkl`
