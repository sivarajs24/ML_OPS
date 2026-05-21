# Decision Tree - Scam Listing Detection

Dataset:
`../House_Rent_Dataset_TN_synthetic_text_1500_preprocessed.csv`

Notebook:
`house_rent_decision_tree_scam_detection.ipynb`

Problem:
Predict whether a rental listing is scam or not scam.

Target:
`Scam_Flag`

Features:
`Rent`, `BHK`, `Size`, `Bathroom`, `Area Type`, `Furnishing Status`, `Tenant Preferred`, `Point of Contact`

Algorithm:
`DecisionTreeClassifier`

Notebook work:
- Load dataset
- Select features and target
- Convert categorical columns using `pd.get_dummies`
- Split train and test data
- Train decision tree model
- Check score, confusion matrix and classification report
- Predict first 5 test records
- Save model

Output:
`house_rent_decision_tree_scam_detection.pkl`
