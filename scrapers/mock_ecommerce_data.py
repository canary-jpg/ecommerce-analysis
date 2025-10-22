import pandas as pd
import numpy as np 
from datetime import datetime, timedelta
import random


np.random.seed(42)
random.seed(42)


#product categories
products = {
    'Laptops': [
        ('Dell XPS 13', 999, 4.5, 1200),
        ('MacBook Air M2', 1199, 4.8, 2500),
        ('HP Pavilion 15', 649, 4.2, 800),
        ('Lenovo ThinkPad', 899, 4.6, 1500),
        ('ASUS VivoBook', 549, 4.0, 600)
    ],
    'Headphones': [
        ('Sony WH-1000XM5', 349, 4.7, 5000),
        ('Apple AirPods Pro', 249, 4.6, 8000),
        ('Bose QuietComfort', 329, 4.5, 3000),
        ('Beats Studio', 299, 4.3, 2000),
        ('JBL Tune', 99, 4.1, 1500)
    ],
    'Monitors': [
        ('LG UltraWide 34"', 599, 4.6, 2000),
        ('Dell UltraSharp 27"', 449, 4.5, 1800),
        ('Samsung Odyssey', 699, 4.7, 2500),
        ('BenQ Designer', 549, 4.4, 900),
        ('ASUS ProArt', 799, 4.6, 1200)
    ]
}

#generate historical price data (90 days)
all_data = []
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

for category, items in products.items():
    for product_name, base_price, rating, review_count in items:
        for day_offset in range(90):
            date = start_date + timedelta(days=day_offset)

            #simulate price changes (+/-10%)
            price_variation = random.uniform(-0.1, 0.1)
            daily_price = base_price * (1 + price_variation)

            if random.random() < 0.2:
                daily_price *= random.uniform(0.8, 0.95)
            
            all_data.append({
                'product_id': f"{category[:3].upper()}--{hash(product_name) % 10000:04d}",
                'product_name': product_name,
                'category': category,
                'price': round(daily_price, 2),
                'base_price': base_price,
                'rating': round(rating + random.uniform(-0.2, 0.2), 1),
                'review_count': review_count + random.randint(-50, 50),
                'scraped_at': date,
                'source': 'mock_store'
            })

df = pd.DataFrame(all_data)
df.to_csv('../data/ecommerce_products.csv', index=False)

print(f"Generated {len(df)} product records")
print(f"\nProducts by category:")
print(df.groupby('category')['product_name'].nunique())
print(f"\nPrice range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
print(f"\nData saved to data/ecommerce_products.csv")