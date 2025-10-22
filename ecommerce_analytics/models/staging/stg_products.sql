SELECT
    product_id,
    product_name,
    category,
    price,
    base_price,
    rating,
    review_count,
    scraped_at::TIMESTAMP as scraped_at,
    source,
    ROUND(((base_price - price) / base_price) * 100, 2) as discount_pct
FROM {{ source('raw', 'products') }}


