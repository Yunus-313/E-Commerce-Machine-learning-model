import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib

print("Loading data...")
df = pd.read_csv('cleaned_master_data.csv')

# --- 1. DATA FILTERING ---
# Keeping products with 1 to 5000 ratings to avoid "noise"
df = df[(df['no_of_ratings'] > 0) & (df['no_of_ratings'] < 5000)]

features = ['actual_price_gbp', 'ratings', 'main_category']
X = df[features]
y = df['no_of_ratings']

X = pd.get_dummies(X, columns=['main_category'])
model_columns = list(X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 2. FEATURE SCALING (New Improvement) ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ... (Keep your data loading and cleaning the same) ...

print("Training a Robust Random Forest (Objective 10)...")
# We increase n_estimators to 200 to give the model more "opinions"
model = RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_leaf=5, random_state=42)
model.fit(X_train_scaled, y_train)

# ... (Keep the evaluation and saving the same) ...

# --- 3. EVALUATION ---
predictions = model.predict(X_test_scaled)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n--- UPDATED MODEL ACCURACY REPORT ---")
print(f"Mean Absolute Error: {mae:.2f} ratings")
print(f"R² Score (Accuracy): {r2:.2%}")
print("--------------------------------------\n")

# --- 4. SAVING (Now saving the scaler too!) ---
model_data = {
    'model': model,
    'columns': model_columns,
    'scaler': scaler
}
joblib.dump(model_data, 'sales_model.pkl')
print("Model and Scaler saved successfully.")