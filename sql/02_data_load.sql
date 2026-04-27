-- ============================================================
-- UK Road Safety Intelligence Platform
-- Script 02: Data Load (SQLite)
-- Run AFTER 01_schema_create.sql
--
-- HOW TO RUN IN DB BROWSER FOR SQLITE:
--   1. File > New Database > save as "road_safety.db" in data/
--   2. File > Import > Table from CSV...
--      - accidents_export.csv  → table: accidents
--      - casualties_export.csv → table: casualties
--      - vehicles_export.csv   → table: vehicles
--      (tick "Column names in first line")
--   3. Run this script for integrity checks & summary counts
--
-- HOW TO RUN FROM COMMAND LINE (sqlite3 must be installed):
--   sqlite3 data/road_safety.db < sql/02_data_load.sql
-- ============================================================

-- ── Post-load integrity checks ────────────────────────────────

-- Row counts (should match Python EDA output)
SELECT 'accidents'  AS tbl, COUNT(*) AS rows FROM accidents
UNION ALL
SELECT 'casualties' AS tbl, COUNT(*) AS rows FROM casualties
UNION ALL
SELECT 'vehicles'   AS tbl, COUNT(*) AS rows FROM vehicles;

-- Check for NULLs in critical columns
SELECT
    SUM(CASE WHEN accident_index   IS NULL THEN 1 ELSE 0 END) AS null_index,
    SUM(CASE WHEN accident_date    IS NULL THEN 1 ELSE 0 END) AS null_date,
    SUM(CASE WHEN accident_severity IS NULL THEN 1 ELSE 0 END) AS null_severity,
    SUM(CASE WHEN year             IS NULL THEN 1 ELSE 0 END) AS null_year
FROM accidents;

-- Year distribution (should be 2019–2023)
SELECT year, COUNT(*) AS accidents, SUM(is_fatal) AS fatalities
FROM accidents
GROUP BY year
ORDER BY year;

-- Severity distribution
SELECT severity_label, COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM accidents), 2) AS pct
FROM accidents
GROUP BY severity_label
ORDER BY count DESC;

-- Duplicate check (should be 0)
SELECT COUNT(*) - COUNT(DISTINCT accident_index) AS duplicate_accidents FROM accidents;

-- Orphan casualties (not linked to an accident) — should be 0
SELECT COUNT(*) AS orphan_casualties
FROM casualties c
LEFT JOIN accidents a ON c.accident_index = a.accident_index
WHERE a.accident_index IS NULL;

SELECT 'Data load verification complete' AS status;
