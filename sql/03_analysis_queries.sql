-- ============================================================
-- UK Road Safety Intelligence Platform
-- Script 03: Analytical Queries
-- These queries answer the core business questions.
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- SECTION A: NATIONAL KPI DASHBOARD
-- ════════════════════════════════════════════════════════════

-- A1. Top-line KPIs (single row summary)
SELECT
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS total_fatal,
    SUM(is_serious)                                     AS total_serious,
    COUNT(*) - SUM(is_fatal) - SUM(is_serious)          AS total_slight,
    SUM(number_of_casualties)                           AS total_casualties,
    ROUND(AVG(number_of_casualties), 2)                 AS avg_casualties_per_accident,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct,
    MIN(year)                                           AS data_from,
    MAX(year)                                           AS data_to
FROM accidents;


-- A2. Annual performance with year-on-year change
WITH yearly AS (
    SELECT
        year,
        COUNT(*)                 AS accidents,
        SUM(is_fatal)            AS fatalities,
        SUM(is_serious)          AS serious,
        SUM(number_of_casualties) AS casualties
    FROM accidents
    GROUP BY year
),
with_yoy AS (
    SELECT
        y.*,
        LAG(y.accidents)   OVER (ORDER BY y.year) AS prev_accidents,
        LAG(y.fatalities)  OVER (ORDER BY y.year) AS prev_fatalities
    FROM yearly y
)
SELECT
    year,
    accidents,
    fatalities,
    serious,
    casualties,
    ROUND(fatalities * 100.0 / accidents, 3)             AS fatality_rate_pct,
    ROUND((accidents - prev_accidents) * 100.0 / prev_accidents, 1) AS yoy_accident_change_pct,
    ROUND((fatalities - prev_fatalities) * 100.0 / prev_fatalities, 1) AS yoy_fatality_change_pct
FROM with_yoy
ORDER BY year;


-- ════════════════════════════════════════════════════════════
-- SECTION B: TIME PATTERN ANALYSIS
-- ════════════════════════════════════════════════════════════

-- B1. Accidents by hour of day (shows rush-hour peaks)
SELECT
    CAST(hour AS INTEGER)                               AS hour_of_day,
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS fatal,
    SUM(is_serious)                                     AS serious,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE hour IS NOT NULL
GROUP BY CAST(hour AS INTEGER)
ORDER BY hour_of_day;


-- B2. Day of week pattern
SELECT
    day_of_week_label,
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS fatalities,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM accidents), 1) AS share_of_total_pct
FROM accidents
WHERE day_of_week_label IS NOT NULL
GROUP BY day_of_week_label
ORDER BY total_accidents DESC;


-- B3. Monthly seasonality (average across all years)
SELECT
    month,
    month_name,
    ROUND(AVG(monthly_count), 0)                        AS avg_accidents_per_month,
    ROUND(AVG(monthly_fatal), 0)                        AS avg_fatalities_per_month
FROM (
    SELECT
        month,
        month_name,
        year,
        COUNT(*) AS monthly_count,
        SUM(is_fatal) AS monthly_fatal
    FROM accidents
    GROUP BY month, month_name, year
) sub
GROUP BY month, month_name
ORDER BY month;


-- B4. Hour × Day matrix (for heatmap visualisation)
SELECT
    day_of_week_label,
    CAST(hour AS INTEGER)                               AS hour_of_day,
    COUNT(*)                                            AS accidents,
    SUM(is_fatal)                                       AS fatalities
FROM accidents
WHERE hour IS NOT NULL AND day_of_week_label IS NOT NULL
GROUP BY day_of_week_label, CAST(hour AS INTEGER)
ORDER BY day_of_week_label, hour_of_day;


-- ════════════════════════════════════════════════════════════
-- SECTION C: GEOGRAPHIC ANALYSIS
-- ════════════════════════════════════════════════════════════

-- C1. Police force ranking (all metrics)
SELECT
    police_force_label,
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS fatalities,
    SUM(is_serious)                                     AS serious,
    SUM(number_of_casualties)                           AS casualties,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct,
    ROUND(COUNT(*) * 1.0 / 5, 0)                        AS avg_accidents_per_year
FROM accidents
WHERE police_force_label IS NOT NULL
GROUP BY police_force_label
ORDER BY total_accidents DESC;


-- C2. Urban vs Rural breakdown
SELECT
    urban_rural_label,
    accident_severity,
    severity_label,
    COUNT(*)                                            AS accidents,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY urban_rural_label), 1) AS pct_within_area
FROM accidents
WHERE urban_rural_label IS NOT NULL
GROUP BY urban_rural_label, accident_severity, severity_label
ORDER BY urban_rural_label, accident_severity;


-- C3. Top 20 local authorities by KSI rate (min 200 accidents)
SELECT
    local_authority_district,
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS fatal,
    SUM(is_serious)                                     AS serious,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE local_authority_district IS NOT NULL
GROUP BY local_authority_district
HAVING COUNT(*) >= 200
ORDER BY ksi_rate_pct DESC
LIMIT 20;


-- ════════════════════════════════════════════════════════════
-- SECTION D: CONDITION-BASED RISK ANALYSIS
-- ════════════════════════════════════════════════════════════

-- D1. Weather conditions risk matrix
SELECT
    weather_label,
    COUNT(*)                                            AS total_accidents,
    SUM(is_fatal)                                       AS fatalities,
    SUM(is_serious)                                     AS serious,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE weather_label IS NOT NULL AND weather_label != 'Unknown'
GROUP BY weather_label
ORDER BY fatality_rate_pct DESC;


-- D2. Road surface conditions
SELECT
    road_surface_label,
    COUNT(*)                                            AS accidents,
    SUM(is_fatal)                                       AS fatalities,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE road_surface_label IS NOT NULL AND road_surface_label != 'Data missing'
GROUP BY road_surface_label
ORDER BY fatality_rate_pct DESC;


-- D3. Speed limit risk profile
SELECT
    speed_limit,
    speed_limit_label,
    COUNT(*)                                            AS accidents,
    SUM(is_fatal)                                       AS fatalities,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE speed_limit IS NOT NULL
GROUP BY speed_limit, speed_limit_label
ORDER BY speed_limit;


-- D4. Combined night + wet road risk (2×2 matrix)
SELECT
    CASE WHEN is_night = 1 THEN 'Night' ELSE 'Daylight' END                 AS light,
    CASE WHEN is_wet_road = 1 THEN 'Wet Road' ELSE 'Dry Road' END           AS surface,
    COUNT(*)                                                                  AS accidents,
    SUM(is_fatal)                                                             AS fatalities,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)                              AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2)            AS ksi_rate_pct
FROM accidents
GROUP BY is_night, is_wet_road
ORDER BY fatality_rate_pct DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION E: VEHICLE & CASUALTY ANALYSIS
-- ════════════════════════════════════════════════════════════

-- E1. Casualty demographics summary
SELECT
    c.casualty_class_label                              AS road_user_type,
    c.age_band,
    c.sex_label,
    COUNT(*)                                            AS casualties,
    SUM(c.is_fatal)                                     AS fatalities,
    SUM(c.is_serious)                                   AS serious,
    ROUND(SUM(c.is_fatal) * 100.0 / COUNT(*), 3)        AS fatality_rate_pct
FROM casualties c
WHERE c.sex_label IN ('Male', 'Female') AND c.age_band IS NOT NULL
GROUP BY c.casualty_class_label, c.age_band, c.sex_label
ORDER BY casualties DESC;


-- E2. Vehicle type involvement in accidents
SELECT
    v.vehicle_type_label,
    COUNT(DISTINCT v.accident_index)                    AS accidents_involved,
    COUNT(*)                                            AS total_vehicles,
    SUM(a.is_fatal)                                     AS in_fatal_accidents,
    ROUND(SUM(a.is_fatal) * 100.0 / COUNT(DISTINCT v.accident_index), 2) AS fatal_involvement_pct
FROM vehicles v
JOIN accidents a ON v.accident_index = a.accident_index
WHERE v.vehicle_type_label IS NOT NULL
GROUP BY v.vehicle_type_label
ORDER BY accidents_involved DESC;


-- E3. Young driver analysis (17-25 year olds)
SELECT
    a.year,
    COUNT(DISTINCT v.accident_index)                    AS accidents_with_young_drivers,
    SUM(a.is_fatal)                                     AS fatalities,
    ROUND(SUM(a.is_fatal) * 100.0 / COUNT(DISTINCT v.accident_index), 3) AS fatality_rate_pct
FROM vehicles v
JOIN accidents a ON v.accident_index = a.accident_index
WHERE v.age_of_driver BETWEEN 17 AND 25
GROUP BY a.year
ORDER BY a.year;


-- ════════════════════════════════════════════════════════════
-- SECTION F: ADVANCED ANALYTICS
-- ════════════════════════════════════════════════════════════

-- F1. Rolling 12-month accident trend
WITH monthly AS (
    SELECT
        year,
        month,
        COUNT(*)      AS accidents,
        SUM(is_fatal) AS fatalities
    FROM accidents
    GROUP BY year, month
),
ordered AS (
    SELECT
        year, month, accidents, fatalities,
        ROW_NUMBER() OVER (ORDER BY year, month) AS rn
    FROM monthly
)
SELECT
    year, month, accidents, fatalities,
    ROUND(AVG(accidents)   OVER (ORDER BY rn ROWS BETWEEN 11 PRECEDING AND CURRENT ROW), 0) AS rolling_12m_accidents,
    ROUND(AVG(fatalities)  OVER (ORDER BY rn ROWS BETWEEN 11 PRECEDING AND CURRENT ROW), 1) AS rolling_12m_fatalities
FROM ordered
ORDER BY year, month;


-- F2. Junction hotspot analysis
SELECT
    junction_label,
    speed_limit_label,
    COUNT(*)                                            AS accidents,
    SUM(is_fatal)                                       AS fatalities,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 2)          AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents
WHERE junction_label IS NOT NULL AND speed_limit_label IS NOT NULL
GROUP BY junction_label, speed_limit_label
HAVING COUNT(*) >= 100
ORDER BY ksi_rate_pct DESC
LIMIT 20;


-- F3. Percentage change 2022 vs 2023 by police force
WITH by_year AS (
    SELECT
        police_force_label,
        year,
        COUNT(*)      AS accidents,
        SUM(is_fatal) AS fatalities
    FROM accidents
    WHERE year IN (2022, 2023)
    GROUP BY police_force_label, year
),
pivoted AS (
    SELECT
        police_force_label,
        SUM(CASE WHEN year = 2022 THEN accidents   ELSE 0 END) AS acc_2022,
        SUM(CASE WHEN year = 2023 THEN accidents   ELSE 0 END) AS acc_2023,
        SUM(CASE WHEN year = 2022 THEN fatalities  ELSE 0 END) AS fat_2022,
        SUM(CASE WHEN year = 2023 THEN fatalities  ELSE 0 END) AS fat_2023
    FROM by_year
    GROUP BY police_force_label
)
SELECT
    police_force_label,
    acc_2022, acc_2023,
    ROUND((acc_2023 - acc_2022) * 100.0 / NULLIF(acc_2022, 0), 1) AS accident_change_pct,
    fat_2022, fat_2023,
    ROUND((fat_2023 - fat_2022) * 100.0 / NULLIF(fat_2022, 0), 1) AS fatality_change_pct
FROM pivoted
ORDER BY accident_change_pct DESC;
