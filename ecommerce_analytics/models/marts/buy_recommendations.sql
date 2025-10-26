WITH insights AS (
    SELECT * FROM {{ ref('product_insights') }}
),

price_trends AS (
    SELECT
        product_id,
        AVG(CASE WHEN price_trend = 'PRICE_DROP' THEN 1 ELSE 0 END) as drop_frequency,
        AVG(CASE WHEN price_trend = 'PRICE_INCREASE' THEN 1 ELSE 0 END) as increase_frequency
    FROM {{ ref('product_price_history') }}
    WHERE price_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1
)

SELECT
    i.product_id,
    i.product_name,
    i.category,
    i.current_price,
    i.historical_low,
    i.deal_rating,
    i.discount_from_avg_pct,
    i.pct_above_low,
    i.price_stability,
    pt.drop_frequency,
    
    -- Calculate recommendation score (0-100)
    ROUND(
        (CASE i.deal_rating
            WHEN 'EXCELLENT_DEAL' THEN 40
            WHEN 'GOOD_DEAL' THEN 25
            WHEN 'FAIR_PRICE' THEN 10
            ELSE 0
        END) +
        (CASE 
            WHEN i.pct_above_low < 5 THEN 30  -- Very close to historical low
            WHEN i.pct_above_low < 10 THEN 20
            WHEN i.pct_above_low < 20 THEN 10
            ELSE 0
        END) +
        (CASE i.price_stability
            WHEN 'STABLE' THEN 15  -- Prefer stable prices
            WHEN 'MODERATE' THEN 10
            ELSE 5
        END) +
        (pt.drop_frequency * 15)  -- Recently dropping prices
    , 0) as buy_score,
    
    -- Action recommendation
    CASE
        WHEN i.pct_above_low < 5 AND i.deal_rating IN ('EXCELLENT_DEAL', 'GOOD_DEAL') THEN 'BUY_NOW'
        WHEN i.deal_rating = 'EXCELLENT_DEAL' THEN 'STRONG_BUY'
        WHEN i.deal_rating = 'GOOD_DEAL' AND pt.drop_frequency > 0.3 THEN 'BUY_SOON'
        WHEN pt.increase_frequency > 0.5 THEN 'WAIT_FOR_DROP'
        ELSE 'MONITOR'
    END as recommendation,
    
    -- Expected savings if waiting
    ROUND(i.current_price - i.historical_low, 2) as potential_savings_dollars,
    
    CURRENT_TIMESTAMP as recommendation_date

FROM insights i
LEFT JOIN price_trends pt ON i.product_id = pt.product_id
ORDER BY buy_score DESC