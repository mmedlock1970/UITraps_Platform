-- Customer activity reports for the UI Traps Analyzer
-- =====================================================
-- Run these against the production Postgres (Railway → Postgres service →
-- "Data"/"Query" tab, or `psql $DATABASE_URL`). All are read-only SELECTs.
--
-- Source of truth: `analysis_reports` — one row per completed analysis, keyed by the
-- stable WordPress user ID (from the JWT). `user_subscriptions` holds each customer's
-- plan/allowance. Tokens & cost live in statistics->'run_details' for analyses run
-- AFTER the run-details persistence change deploys (earlier reports have counts only).


-- ─────────────────────────────────────────────────────────────────────────────
-- 1) PER-CUSTOMER ACTIVITY  (works on all existing data)
--    How many analyses each customer has run, when, and of what type.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.user_id,
    COALESCE(s.subscription_status, 'unknown')                      AS status,
    s.monthly_limit,
    s.monthly_used,
    s.bonus_tokens,
    COUNT(*)                                                        AS analyses,
    MIN(r.timestamp)                                                AS first_analysis,
    MAX(r.timestamp)                                                AS last_analysis,
    COUNT(*) FILTER (WHERE r.analysis_type = 'single_image')        AS single_image,
    COUNT(*) FILTER (WHERE r.analysis_type = 'multi_image')         AS multi_image
FROM analysis_reports r
LEFT JOIN user_subscriptions s ON s.user_id = r.user_id
GROUP BY r.user_id, s.subscription_status, s.monthly_limit, s.monthly_used, s.bonus_tokens
ORDER BY analyses DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- 1b) EVERY ANALYSIS, NEWEST FIRST  (the raw activity log)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    user_id,
    timestamp,
    analysis_type,
    design_name,
    file_name
FROM analysis_reports
ORDER BY timestamp DESC
LIMIT 500;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2) PER-ANALYSIS RUN DETAILS  (analyses run AFTER the persistence change)
--    Model, estimated cost, tokens, duration, and issues found per report.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    user_id,
    timestamp,
    analysis_type,
    design_name,
    statistics::jsonb -> 'run_details' ->> 'model'                        AS model,
    (statistics::jsonb -> 'run_details' ->> 'estimated_cost')::numeric    AS est_cost_usd,
    (statistics::jsonb -> 'run_details' ->> 'tokens_total')::int          AS tokens_total,
    (statistics::jsonb -> 'run_details' ->> 'duration_seconds')::numeric  AS seconds,
    (statistics::jsonb ->> 'total_issues')::int                           AS issues_found
FROM analysis_reports
WHERE statistics IS NOT NULL
  AND statistics::jsonb ? 'run_details'
ORDER BY timestamp DESC
LIMIT 500;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2b) PER-CUSTOMER COST & TOKEN ROLLUP  (analyses run AFTER the change)
--    What each customer has cost you in API spend (estimated).
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    user_id,
    COUNT(*)                                                                               AS analyses,
    ROUND(SUM((statistics::jsonb -> 'run_details' ->> 'estimated_cost')::numeric), 4)      AS total_est_cost_usd,
    SUM((statistics::jsonb -> 'run_details' ->> 'tokens_total')::int)                      AS total_tokens,
    ROUND(AVG((statistics::jsonb -> 'run_details' ->> 'estimated_cost')::numeric), 4)      AS avg_cost_per_analysis
FROM analysis_reports
WHERE statistics IS NOT NULL
  AND statistics::jsonb ? 'run_details'
GROUP BY user_id
ORDER BY total_est_cost_usd DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2c) GRAND TOTALS  (estimated spend captured in-app, after the change)
--    Cross-check against console.anthropic.com → Usage for the authoritative bill.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                                                           AS analyses_with_details,
    COUNT(DISTINCT user_id)                                                            AS distinct_customers,
    ROUND(SUM((statistics::jsonb -> 'run_details' ->> 'estimated_cost')::numeric), 4)  AS total_est_cost_usd,
    SUM((statistics::jsonb -> 'run_details' ->> 'tokens_total')::int)                  AS total_tokens
FROM analysis_reports
WHERE statistics IS NOT NULL
  AND statistics::jsonb ? 'run_details';
