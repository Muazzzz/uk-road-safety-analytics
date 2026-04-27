-- ============================================================
-- UK Road Safety Intelligence Platform
-- Script 04: Reusable Views & Summary Reports
-- These views power the Power BI and Excel connections.
-- ============================================================


-- ── Power BI / Excel connector views ─────────────────────────

-- vw_accident_summary  — one row per accident, fully labelled
-- (use as the main fact table in Power BI)
CREATE VIEW IF NOT EXISTS vw_accident_summary AS
SELECT
    a.accident_index,
    a.accident_date,
    a.year,
    a.quarter,
    a.month,
    a.month_name,
    a.day_of_week_label,
    a.hour,
    a.time_band,
    a.is_weekend,
    a.severity_label,
    a.is_fatal,
    a.is_serious,
    CASE WHEN a.is_fatal = 0 AND a.is_serious = 0 THEN 1 ELSE 0 END AS is_slight,
    a.number_of_casualties,
    a.number_of_vehicles,
    a.police_force_label,
    COALESCE(pf.region, 'Unknown')                                   AS region,
    a.local_authority_district,
    a.urban_rural_label,
    a.speed_limit,
    a.speed_limit_label,
    a.road_type_label,
    a.junction_label,
    a.light_label,
    a.weather_label,
    a.road_surface_label,
    a.is_night,
    a.is_wet_road,
    a.latitude,
    a.longitude
FROM accidents a
LEFT JOIN dim_police_force pf ON a.police_force_label = pf.force_name;


-- vw_kpi_by_year  — annual headline metrics for card visuals
CREATE VIEW IF NOT EXISTS vw_kpi_by_year AS
SELECT
    year,
    COUNT(*)                                                        AS accidents,
    SUM(is_fatal)                                                   AS fatalities,
    SUM(is_serious)                                                 AS serious,
    COUNT(*) - SUM(is_fatal) - SUM(is_serious)                      AS slight,
    SUM(number_of_casualties)                                       AS casualties,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)                      AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2)    AS ksi_rate_pct,
    ROUND(AVG(number_of_casualties), 3)                             AS avg_casualties_per_accident
FROM accidents
GROUP BY year;


-- vw_hourly_pattern  — for time-of-day line charts
CREATE VIEW IF NOT EXISTS vw_hourly_pattern AS
SELECT
    CAST(hour AS INTEGER)                                           AS hour_of_day,
    COUNT(*)                                                        AS accidents,
    SUM(is_fatal)                                                   AS fatalities,
    SUM(is_serious)                                                 AS serious,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)                      AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2)    AS ksi_rate_pct
FROM accidents
WHERE hour IS NOT NULL
GROUP BY CAST(hour AS INTEGER);


-- vw_region_metrics  — for map and bar visuals
CREATE VIEW IF NOT EXISTS vw_region_metrics AS
SELECT
    a.police_force_label,
    COALESCE(pf.region, 'Unknown')                                  AS region,
    COUNT(*)                                                        AS accidents,
    SUM(a.is_fatal)                                                 AS fatalities,
    SUM(a.is_serious)                                               AS serious,
    SUM(a.number_of_casualties)                                     AS casualties,
    ROUND(SUM(a.is_fatal) * 100.0 / COUNT(*), 3)                    AS fatality_rate_pct,
    ROUND((SUM(a.is_fatal)+SUM(a.is_serious)) * 100.0 / COUNT(*), 2) AS ksi_rate_pct
FROM accidents a
LEFT JOIN dim_police_force pf ON a.police_force_label = pf.force_name
WHERE a.police_force_label IS NOT NULL
GROUP BY a.police_force_label, pf.region;


-- vw_conditions_risk  — condition-based risk for cross-filter visuals
CREATE VIEW IF NOT EXISTS vw_conditions_risk AS
SELECT
    weather_label,
    road_surface_label,
    light_label,
    speed_limit_label,
    urban_rural_label,
    COUNT(*)                                                        AS accidents,
    SUM(is_fatal)                                                   AS fatalities,
    SUM(is_serious)                                                 AS serious,
    ROUND(SUM(is_fatal) * 100.0 / COUNT(*), 3)                      AS fatality_rate_pct,
    ROUND((SUM(is_fatal)+SUM(is_serious)) * 100.0 / COUNT(*), 2)    AS ksi_rate_pct
FROM accidents
GROUP BY weather_label, road_surface_label, light_label, speed_limit_label, urban_rural_label;


-- vw_monthly_trend  — for time-series line chart
CREATE VIEW IF NOT EXISTS vw_monthly_trend AS
SELECT
    year,
    month,
    month_name,
    COUNT(*)                                                        AS accidents,
    SUM(is_fatal)                                                   AS fatalities,
    SUM(is_serious)                                                 AS serious,
    SUM(number_of_casualties)                                       AS casualties
FROM accidents
GROUP BY year, month, month_name
ORDER BY year, month;


-- vw_vehicle_risk  — for vehicle type analysis
CREATE VIEW IF NOT EXISTS vw_vehicle_risk AS
SELECT
    v.vehicle_type_label,
    COUNT(DISTINCT v.accident_index)                                AS accidents_involved,
    COUNT(*)                                                        AS total_vehicles,
    SUM(a.is_fatal)                                                 AS in_fatal_accidents,
    SUM(a.is_serious)                                               AS in_serious_accidents,
    ROUND(SUM(a.is_fatal) * 100.0 / COUNT(DISTINCT v.accident_index), 2) AS fatal_pct,
    ROUND((SUM(a.is_fatal)+SUM(a.is_serious)) * 100.0 / COUNT(DISTINCT v.accident_index), 2) AS ksi_pct
FROM vehicles v
JOIN accidents a ON v.accident_index = a.accident_index
WHERE v.vehicle_type_label IS NOT NULL
GROUP BY v.vehicle_type_label;


-- vw_casualty_demographics
CREATE VIEW IF NOT EXISTS vw_casualty_demographics AS
SELECT
    c.casualty_class_label,
    c.age_band,
    c.sex_label,
    c.casualty_severity_label,
    COUNT(*)                                                        AS casualties,
    SUM(c.is_fatal)                                                 AS fatalities
FROM casualties c
WHERE c.sex_label IN ('Male', 'Female')
GROUP BY c.casualty_class_label, c.age_band, c.sex_label, c.casualty_severity_label;


-- ── Final verification ─────────────────────────────────────────

SELECT name AS view_name
FROM sqlite_master
WHERE type = 'view'
ORDER BY name;

SELECT 'All views created. Database ready for Power BI and Excel.' AS status;
