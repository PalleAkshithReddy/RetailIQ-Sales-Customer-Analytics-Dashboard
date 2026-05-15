-- ============================================================
-- RetailIQ – SQL Analytics Query Library
-- Database: PostgreSQL / MySQL compatible
-- Author: RetailIQ Analytics Team
-- ============================================================

-- ── TABLE CREATION ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS customers (
    customer_id       VARCHAR(10) PRIMARY KEY,
    name              VARCHAR(100),
    email             VARCHAR(100),
    phone             VARCHAR(20),
    city              VARCHAR(50),
    state             VARCHAR(50),
    age               INT,
    gender            VARCHAR(10),
    segment           VARCHAR(20),
    join_date         DATE,
    is_loyalty_member BOOLEAN
);

CREATE TABLE IF NOT EXISTS products (
    product_id    VARCHAR(10) PRIMARY KEY,
    product_name  VARCHAR(100),
    category      VARCHAR(50),
    brand         VARCHAR(50),
    unit_price    DECIMAL(10,2),
    cost_price    DECIMAL(10,2),
    stock_qty     INT,
    supplier_city VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stores (
    store_id   VARCHAR(10) PRIMARY KEY,
    store_name VARCHAR(100),
    city       VARCHAR(50),
    region     VARCHAR(20),
    size_sqft  INT,
    manager    VARCHAR(100),
    open_date  DATE
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(12) PRIMARY KEY,
    customer_id    VARCHAR(10),
    product_id     VARCHAR(10),
    store_id       VARCHAR(10),
    date           DATE,
    month          INT,
    year           INT,
    quarter        VARCHAR(5),
    quantity       INT,
    unit_price     DECIMAL(10,2),
    discount_pct   DECIMAL(5,2),
    discount_amt   DECIMAL(10,2),
    total_amount   DECIMAL(12,2),
    cost_amount    DECIMAL(12,2),
    profit         DECIMAL(12,2),
    payment_method VARCHAR(20),
    channel        VARCHAR(20),
    is_returned    BOOLEAN,
    return_reason  VARCHAR(50),
    rating         INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (store_id)    REFERENCES stores(store_id)
);


-- ════════════════════════════════════════════════════════════
-- SECTION 1: REVENUE & PROFIT KPIs
-- ════════════════════════════════════════════════════════════

-- Q1.1 Overall Business KPIs
SELECT
    COUNT(DISTINCT transaction_id)            AS total_transactions,
    COUNT(DISTINCT customer_id)               AS unique_customers,
    ROUND(SUM(total_amount), 0)               AS total_revenue,
    ROUND(SUM(profit), 0)                     AS total_profit,
    ROUND(SUM(profit)/SUM(total_amount)*100, 2) AS profit_margin_pct,
    ROUND(AVG(total_amount), 2)               AS avg_order_value,
    ROUND(AVG(rating), 2)                     AS avg_rating,
    ROUND(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END)::FLOAT
          / COUNT(*) * 100, 2)                AS return_rate_pct
FROM transactions;


-- Q1.2 Monthly Revenue & Profit Trend
SELECT
    year,
    month,
    TO_CHAR(DATE_TRUNC('month', date), 'Mon YYYY') AS month_label,
    ROUND(SUM(total_amount), 0)                     AS revenue,
    ROUND(SUM(profit), 0)                           AS profit,
    ROUND(SUM(profit)/SUM(total_amount)*100, 2)     AS margin_pct,
    COUNT(*)                                        AS transactions
FROM transactions
GROUP BY year, month, DATE_TRUNC('month', date)
ORDER BY year, month;


-- Q1.3 Year-over-Year Revenue Comparison
SELECT
    year,
    ROUND(SUM(total_amount), 0) AS revenue,
    ROUND(SUM(profit), 0)       AS profit,
    COUNT(*)                    AS transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(AVG(total_amount), 2) AS avg_order_value
FROM transactions
GROUP BY year
ORDER BY year;


-- Q1.4 Quarterly Revenue with Growth Rate
WITH quarterly AS (
    SELECT
        year, quarter,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM transactions
    GROUP BY year, quarter
)
SELECT
    year, quarter, revenue,
    LAG(revenue) OVER (PARTITION BY quarter ORDER BY year) AS prev_year_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY quarter ORDER BY year))
        / NULLIF(LAG(revenue) OVER (PARTITION BY quarter ORDER BY year), 0) * 100,
    2) AS yoy_growth_pct
FROM quarterly
ORDER BY year, quarter;


-- ════════════════════════════════════════════════════════════
-- SECTION 2: PRODUCT & CATEGORY ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Q2.1 Revenue & Profit by Category
SELECT
    p.category,
    COUNT(t.transaction_id)              AS transactions,
    ROUND(SUM(t.total_amount), 0)        AS revenue,
    ROUND(SUM(t.profit), 0)              AS profit,
    ROUND(SUM(t.profit)/SUM(t.total_amount)*100, 2) AS margin_pct,
    ROUND(AVG(t.total_amount), 2)        AS avg_order_value,
    ROUND(AVG(t.rating), 2)              AS avg_rating,
    ROUND(SUM(CASE WHEN t.is_returned THEN 1 ELSE 0 END)::FLOAT
          / COUNT(*) * 100, 2)           AS return_rate_pct
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- Q2.2 Top 10 Products by Revenue
SELECT
    p.product_name,
    p.category,
    COUNT(t.transaction_id)       AS transactions,
    SUM(t.quantity)               AS units_sold,
    ROUND(SUM(t.total_amount), 0) AS revenue,
    ROUND(SUM(t.profit), 0)       AS profit,
    ROUND(AVG(t.rating), 2)       AS avg_rating
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;


-- Q2.3 Product Performance with ABC Classification
WITH product_revenue AS (
    SELECT
        p.product_id, p.product_name, p.category,
        ROUND(SUM(t.total_amount), 0) AS revenue
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
),
ranked AS (
    SELECT *,
        SUM(revenue) OVER ()                                              AS total_rev,
        SUM(revenue) OVER (ORDER BY revenue DESC)                         AS cumulative_rev,
        SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER () AS cum_pct
    FROM product_revenue
)
SELECT
    product_name, category, revenue,
    ROUND(cum_pct * 100, 1) AS cumulative_pct,
    CASE
        WHEN cum_pct <= 0.80 THEN 'A – High Value'
        WHEN cum_pct <= 0.95 THEN 'B – Medium Value'
        ELSE 'C – Low Value'
    END AS abc_class
FROM ranked
ORDER BY revenue DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 3: CUSTOMER ANALYTICS
-- ════════════════════════════════════════════════════════════

-- Q3.1 Customer Segment Revenue Summary
SELECT
    c.segment,
    COUNT(DISTINCT t.customer_id)         AS customers,
    COUNT(t.transaction_id)               AS transactions,
    ROUND(SUM(t.total_amount), 0)         AS revenue,
    ROUND(AVG(t.total_amount), 2)         AS avg_order_value,
    ROUND(SUM(t.total_amount) / COUNT(DISTINCT t.customer_id), 2) AS revenue_per_customer
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;


-- Q3.2 Loyalty vs Non-Loyalty Customer Spend
SELECT
    c.is_loyalty_member,
    COUNT(DISTINCT t.customer_id)  AS customers,
    COUNT(t.transaction_id)        AS transactions,
    ROUND(SUM(t.total_amount), 0)  AS revenue,
    ROUND(AVG(t.total_amount), 2)  AS avg_order_value,
    ROUND(AVG(t.rating), 2)        AS avg_rating
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.is_loyalty_member;


-- Q3.3 RFM Analysis – Customer Value Scoring
WITH rfm_raw AS (
    SELECT
        customer_id,
        MAX(date)                                AS last_purchase,
        COUNT(transaction_id)                    AS frequency,
        ROUND(SUM(total_amount), 2)              AS monetary,
        CURRENT_DATE - MAX(date)                 AS recency_days
    FROM transactions
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC)   AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)       AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)        AS m_score
    FROM rfm_raw
)
SELECT
    customer_id,
    recency_days, frequency, monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 13 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Loyal Customers'
        WHEN (r_score + f_score + m_score) >= 7  THEN 'Potential Loyalists'
        WHEN (r_score + f_score + m_score) >= 4  THEN 'At Risk'
        ELSE 'Lost Customers'
    END AS rfm_segment
FROM rfm_scored
ORDER BY rfm_total DESC;


-- Q3.4 Customer Lifetime Value (CLV)
SELECT
    c.customer_id, c.name, c.segment, c.city,
    COUNT(t.transaction_id)         AS total_orders,
    ROUND(SUM(t.total_amount), 2)   AS total_spent,
    ROUND(AVG(t.total_amount), 2)   AS avg_order_value,
    MIN(t.date)                     AS first_purchase,
    MAX(t.date)                     AS last_purchase,
    MAX(t.date) - MIN(t.date)       AS customer_lifespan_days
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.customer_id, c.name, c.segment, c.city
ORDER BY total_spent DESC
LIMIT 20;


-- Q3.5 Age Group Revenue Analysis
SELECT
    CASE
        WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
        WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
        WHEN c.age BETWEEN 36 AND 45 THEN '36-45'
        WHEN c.age BETWEEN 46 AND 55 THEN '46-55'
        ELSE '56+'
    END AS age_group,
    COUNT(DISTINCT t.customer_id)   AS customers,
    COUNT(t.transaction_id)         AS transactions,
    ROUND(SUM(t.total_amount), 0)   AS revenue,
    ROUND(AVG(t.total_amount), 2)   AS avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY age_group
ORDER BY age_group;


-- ════════════════════════════════════════════════════════════
-- SECTION 4: STORE & REGIONAL ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Q4.1 Store Performance Ranking
SELECT
    s.store_name, s.city, s.region,
    COUNT(t.transaction_id)              AS transactions,
    COUNT(DISTINCT t.customer_id)        AS unique_customers,
    ROUND(SUM(t.total_amount), 0)        AS revenue,
    ROUND(SUM(t.profit), 0)              AS profit,
    ROUND(SUM(t.profit)/SUM(t.total_amount)*100, 2) AS margin_pct,
    DENSE_RANK() OVER (ORDER BY SUM(t.total_amount) DESC) AS revenue_rank
FROM transactions t
JOIN stores s ON t.store_id = s.store_id
GROUP BY s.store_name, s.city, s.region
ORDER BY revenue DESC;


-- Q4.2 Regional Revenue Summary
SELECT
    s.region,
    COUNT(DISTINCT s.store_id)     AS stores,
    COUNT(t.transaction_id)        AS transactions,
    ROUND(SUM(t.total_amount), 0)  AS revenue,
    ROUND(AVG(t.total_amount), 2)  AS avg_order_value
FROM transactions t
JOIN stores s ON t.store_id = s.store_id
GROUP BY s.region
ORDER BY revenue DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 5: PAYMENT & CHANNEL ANALYTICS
-- ════════════════════════════════════════════════════════════

-- Q5.1 Payment Method Analysis
SELECT
    payment_method,
    COUNT(*)                      AS transactions,
    ROUND(SUM(total_amount), 0)   AS revenue,
    ROUND(AVG(total_amount), 2)   AS avg_order_value,
    ROUND(AVG(discount_pct), 2)   AS avg_discount_pct,
    ROUND(AVG(rating), 2)         AS avg_rating
FROM transactions
GROUP BY payment_method
ORDER BY revenue DESC;


-- Q5.2 Channel Performance
SELECT
    channel,
    COUNT(*)                       AS transactions,
    ROUND(SUM(total_amount), 0)    AS revenue,
    ROUND(AVG(total_amount), 2)    AS avg_order_value,
    ROUND(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END)::FLOAT
          / COUNT(*) * 100, 2)     AS return_rate_pct
FROM transactions
GROUP BY channel
ORDER BY revenue DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 6: DISCOUNT & RETURN ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Q6.1 Discount Impact on Revenue
SELECT
    discount_pct,
    COUNT(*)                      AS transactions,
    ROUND(AVG(total_amount), 2)   AS avg_order_value,
    ROUND(SUM(total_amount), 0)   AS total_revenue,
    ROUND(AVG(profit), 2)         AS avg_profit,
    ROUND(AVG(rating), 2)         AS avg_rating
FROM transactions
GROUP BY discount_pct
ORDER BY discount_pct;


-- Q6.2 Return Analysis by Category
SELECT
    p.category,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN t.is_returned THEN 1 ELSE 0 END) AS returns,
    ROUND(SUM(CASE WHEN t.is_returned THEN 1 ELSE 0 END)::FLOAT
          / COUNT(*) * 100, 2) AS return_rate_pct,
    t.return_reason,
    COUNT(*) FILTER (WHERE t.return_reason IS NOT NULL) AS reason_count
FROM transactions t
JOIN products p ON t.product_id = p.product_id
WHERE t.is_returned = TRUE
GROUP BY p.category, t.return_reason
ORDER BY return_rate_pct DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 7: ADVANCED ANALYTICS
-- ════════════════════════════════════════════════════════════

-- Q7.1 Moving Average Revenue (3-month)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', date) AS month,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM transactions
    GROUP BY DATE_TRUNC('month', date)
)
SELECT
    month,
    revenue,
    ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0) AS moving_avg_3m
FROM monthly
ORDER BY month;


-- Q7.2 Customer Churn Indicator (no purchase in 90 days)
WITH last_purchase AS (
    SELECT
        customer_id,
        MAX(date) AS last_date
    FROM transactions
    GROUP BY customer_id
)
SELECT
    c.customer_id, c.name, c.segment, c.city,
    lp.last_date,
    CURRENT_DATE - lp.last_date AS days_since_purchase,
    CASE
        WHEN CURRENT_DATE - lp.last_date > 180 THEN 'High Risk Churn'
        WHEN CURRENT_DATE - lp.last_date > 90  THEN 'At Risk'
        ELSE 'Active'
    END AS churn_status
FROM customers c
JOIN last_purchase lp ON c.customer_id = lp.customer_id
ORDER BY days_since_purchase DESC;


-- Q7.3 Market Basket – Co-purchased Products
SELECT
    p1.product_name  AS product_a,
    p2.product_name  AS product_b,
    COUNT(*)         AS co_purchase_count
FROM transactions t1
JOIN transactions t2
    ON t1.customer_id = t2.customer_id
    AND t1.date = t2.date
    AND t1.product_id < t2.product_id
JOIN products p1 ON t1.product_id = p1.product_id
JOIN products p2 ON t2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
HAVING COUNT(*) >= 5
ORDER BY co_purchase_count DESC
LIMIT 20;
