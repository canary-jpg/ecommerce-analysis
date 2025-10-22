import duckdb
import pandas as pd

# Connect to DuckDB - use the path from dbt profile
conn = duckdb.connect('ecommerce_analytics/ecommerce_analytics.duckdb')

# Load CSV data
df = pd.read_csv('data/ecommerce_products.csv')

print(f"Loading {len(df)} records into DuckDB...")
print(f"Columns in CSV: {df.columns.tolist()}")

# Drop table if exists and recreate from DataFrame
conn.execute("DROP TABLE IF EXISTS raw_products")

# Register DataFrame and create table from it
conn.register('df_view', df)
conn.execute("CREATE TABLE raw_products AS SELECT * FROM df_view")

# Verify
count = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()[0]
print(f"✅ Loaded {count} records into raw_products table")

# Show sample
print("\nSample data:")
print(conn.execute("SELECT * FROM raw_products LIMIT 5").df())

conn.close()