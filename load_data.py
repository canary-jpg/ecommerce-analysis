import duckdb
import pandas as pd

# Connect to the database dbt is using
conn = duckdb.connect('ecommerce_analytics/dev.duckdb')

# Load CSV data
df = pd.read_csv('data/ecommerce_products.csv')

print(f"Loading {len(df)} records into dev.duckdb...")
print(f"Columns in CSV: {df.columns.tolist()}")

# Drop and recreate
conn.execute("DROP TABLE IF EXISTS raw_products")
conn.register('df_view', df)
conn.execute("CREATE TABLE raw_products AS SELECT * FROM df_view")

# Verify
count = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()[0]
print(f"✅ Successfully loaded {count} records into raw_products")

# Show sample
print("\nSample data:")
print(conn.execute("SELECT * FROM raw_products LIMIT 3").df())

conn.close()