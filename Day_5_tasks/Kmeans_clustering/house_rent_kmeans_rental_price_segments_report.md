# K-Means - Rental Price Segment Clustering

Dataset:
`../House_Rent_Dataset_TN_synthetic_text_1500_preprocessed.csv`

Notebook:
`house_rent_kmeans_rental_price_segments.ipynb`

Problem:
Group rental houses into low, medium and high rental price segments.

Columns used:
`Rent`, `Size`, `BHK`, `Bathroom`

Algorithm:
`KMeans`

Notebook work:
- Load dataset
- Select rent and house-size related columns
- Plot `Rent` vs `Size`
- Scale values using `MinMaxScaler`
- Train K-Means with 3 clusters
- Add cluster result to dataframe
- Plot rental price segments
- Show cluster averages
- Use elbow method plot
- Predict cluster for a new house
- Save model

Output:
`house_rent_kmeans_rental_price_segments.pkl`
