WITH daily_prices AS (
    SELECT
        product_id,
        product_name,
        category,
        DATE(scraped_at) as price_date,
        AVG(price) as avg_price,
        MIN(price) as min_price,
        MAX(price) as max_price,
        AVG(rating) as avg_rating
    FROM {{ ref('stg_products') }}
    GROUP BY 1, 2, 3, 4
),

price_changes AS (
    SELECT
        *,
        LAG(avg_price) OVER (PARTITION BY product_id ORDER BY price_date) as prev_price,
        avg_price - LAG(avg_price) OVER (PARTITION BY product_id ORDER BY price_date) as price_change 
    FROM daily_prices
)

SELECT 
    *,
    CASE 
        WHEN prev_price IS NOT NULL AND price_change < 0 THEN 'PRICE_DROP'
        WHEN prev_price IS NOT NULL AND price_change > 0 THEN 'PRICE_INCREASE'
        ELSE 'NO_CHANGE'
    END as price_trend
FROM price_changes
ORDER BY product_id, price_date DESC 