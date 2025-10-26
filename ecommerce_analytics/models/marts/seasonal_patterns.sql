WITH daily_data AS (
    SELECT
        product_id,
        product_name,
        category,
        price_date,
        avg_price,
        DAYOFWEEK(price_date) as day_of_week,
        WEEK(price_date) as week_of_year,
        MONTH(price_date) as month 
    FROM {{ ref('product_price_history') }}
),

day_of_week_patterns AS (
    SELECT 
        product_id,
        product_name,
        day_of_week,
        AVG(avg_price) as avg_price_by_day,
        MIN(avg_price) as min_price_by_day,
        COUNT(*) as observations
    FROM daily_data
    GROUP BY 1, 2, 3
),

best_days AS (
    SELECT
        product_id,
        day_of_week as best_day_to_buy,
        avg_price_by_day as best_day_price
    FROM day_of_week_patterns
    QUALIFY ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY avg_price_by_day) = 1
)

SELECT
    dd.product_id,
    dd.product_name,
    dd.category,
    bd.best_day_to_buy,
    CASE bd.best_day_to_buy
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END as best_day_name,
    bd.best_day_price,
    AVG(dd.avg_price) as overall_avg_price,
    ROUND(((AVG(dd.avg_price) - bd.best_day_price) / AVG(dd.avg_price)) * 100, 2) as potential_savings_pct
FROM daily_data dd
JOIN best_days bd ON dd.product_id = bd.product_id
GROUP BY 1, 2, 3, 4, 5, 6