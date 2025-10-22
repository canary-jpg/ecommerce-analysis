import duckdb
import pandas as pd 
import os

db_path = 'ecommerce_analytics/ecommerce_analytics.duckdb'
csv_path = 'data/ecommerce_products.csv'

#check if CSV exists
if not os.path.exists(csv_path):
    print(f"❌ Error: {csv_path} not found. Run scrapers/mock_ecommerce_data.py first!")
    exit(1)

#connect to duckdb
conn = duckdb.connect(db_path)

#check if table exists and has data
try:
    count = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()[0]
    print(f"✅ Table exists with {count} records")

    if count == 0:
        print("⚠️ Table is empty, reloading data...")
        reload = True
    else:
        reload = False
except:
    print("⚠️ Table does not exist, creating and loading...")
    reload = True


if reload:
    df = pd.read_csv(csv_path)
    print(f"Loading {len(df)} records from CSV...")

    #drop and recreate
    conn.execute("DROP TABLE IF EXISTS raw_products")
    conn.register('df_view', df)
    conn.execute("CREATE TABLE raw_products AS SELECT * FROM df_view")

    #verify
    count = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()[0]
    print(f"✅ Successfully loaded {count} records")


#show sample
print("\nSample Data:")
print(conn.execute("SELECT * FROM raw_products LIMIT 3").df())