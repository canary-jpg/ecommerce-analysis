WITH price_stats AS (
    SELECT
        product_id,
        product_name,
        category,
        AVG(avg_price) as overall_avg_price,
        MIN(min_price) as historical_low,
        MAX(max_price) as historical_high,
        STDDEV(avg_price) as price_volatility,
        COUNT(*) as days_tracked
    FROM {{ ref('product_price_history') }}
    GROUP BY 1, 2, 3
),

current_prices AS (
    SELECT
        product_id,
        avg_price as current_price,
        price_date as last_updated
    FROM {{ ref('product_price_history') }}
    QUALIFY ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price_date DESC) = 1
),

price_percentiles AS (
    SELECT
        product_id,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY avg_price) as price_25th_percentile,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY avg_price) as price_median,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY avg_price) as price_75th_percentile
    FROM {{ ref('product_price_history') }}
    GROUP BY 1
)

SELECT
    ps.product_id,
    ps.product_name,
    ps.category,
    cp.current_price,
    ps.overall_avg_price,
    ps.historical_low,
    ps.historical_high,
    ps.price_volatility,
    pp.price_median,
    pp.price_25th_percentile,
    pp.price_75th_percentile,
    ROUND(((ps.overall_avg_price - cp.current_price) / ps.overall_avg_price) * 100, 2) as discount_from_avg_pct,
    ROUND(((cp.current_price - ps.historical_low) / ps.historical_low) * 100, 2) as pct_above_low,
    CASE
        WHEN cp.current_price <= pp.price_25th_percentile THEN 'EXCELLECT_DEAL'
        WHEN cp.current_price <= pp.price_median THEN 'GOOD_DEAL'
        WHEN cp.current_price <= pp.price_75th_percentile THEN 'FAIR_PRICE'
        ELSE 'EXPENSIVE'
    END as deal_rating,
    CASE
        WHEN ps.price_volatility / ps.overall_avg_price < 0.05 THEN 'STABLE'
        WHEN ps.price_volatility / ps.overall_avg_price < 0.15 THEN 'MODERATE'
        ELSE 'VOLATILE'
    END as price_stability,
    ps.days_tracked,
    cp.last_updated
FROM price_stats ps 
JOIN current_prices cp ON ps.product_id = cp.product_id
JOIN price_percentiles pp ON ps.product_id = pp.product_id