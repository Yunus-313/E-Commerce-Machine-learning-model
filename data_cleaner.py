import pandas as pd

print("Loading your data...")
df = pd.read_csv('master_amazon_data.csv')

# --- 1. CLEANING PRICES & ROUNDING ---
def clean_to_pounds(price_str):
    if isinstance(price_str, str):
        clean_str = price_str.replace('₹', '').replace(',', '').strip()
        try:
            # We add .round(2) here to keep it to 2 decimal places
            return round(float(clean_str) * 0.0095, 2)
        except:
            return None
    return None

# --- 2. CLEANING RATINGS (Turning "4.2 out of 5" into 4.2) ---
def clean_rating(rating_val):
    if isinstance(rating_val, str):
        try:
            # Usually looks like "4.2" or "4.2 out of 5"
            return float(rating_val.split()[0])
        except:
            return None
    return rating_val

# --- 3. CLEANING NUMBER OF RATINGS (Removing commas) ---
def clean_no_of_ratings(val):
    if isinstance(val, str):
        try:
            return int(val.replace(',', ''))
        except:
            return None
    return val

print("Cleaning prices, ratings, and counts...")

# Apply the price cleaning and rounding
df['actual_price_gbp'] = df['actual_price'].apply(clean_to_pounds)
df['discount_price_gbp'] = df['discount_price'].apply(clean_to_pounds)

# Apply rating cleaning
df['ratings'] = df['ratings'].apply(clean_rating)
df['no_of_ratings'] = df['no_of_ratings'].apply(clean_no_of_ratings)

# Remove rows that are empty in these crucial columns
df = df.dropna(subset=['actual_price_gbp', 'ratings', 'no_of_ratings'])

# Show the clean results
print("\nSuccess! Look at the nice clean numbers now:")
print(df[['name', 'actual_price_gbp', 'ratings', 'no_of_ratings']].head())

# Save the final 'Gold' version
df.to_csv('cleaned_master_data.csv', index=False)
print(f"\nFinal count: {len(df)} high-quality products saved.")