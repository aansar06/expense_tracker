import pandas as pd

# Load your CSV
df = pd.read_csv("transactions_dataset.csv")

# Define your convenience stores (fixing missing commas)
convenience_stores = ["7-ELEVEN", "MOBIL", "MILITO'S", "WALGREENS", 'CIRCLE K', 'CVS', 'BP', 'CITGO']

# Ensure comparison is case-insensitive
df['merchant_upper'] = df['merchant'].str.upper()

# Replace category for convenience stores
df.loc[df['merchant_upper'].isin(convenience_stores), 'merchant_category'] = "Snacks/Convenience Stores"

# Drop the temporary uppercase column
df = df.drop(columns=['merchant_upper'])

# Save back to CSV
df.to_csv("transactions_dataset_updated.csv", index=False)

print("✅ Merchant categories updated for convenience stores")
