-- ============================================================
-- UK Road Safety Intelligence Platform
-- Script 01: Schema Creation (SQLite compatible)
-- Run this first, then 02_data_load.sql
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;


-- ── Core fact tables ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS accidents (
    -- Primary key
    accident_index              TEXT PRIMARY KEY,

    -- Time dimensions
    accident_date               TEXT,
    year                        INTEGER,
    month                       INTEGER,
    month_name                  TEXT,
    quarter                     INTEGER,
    day_of_week_label           TEXT,
    hour                        REAL,
    time_band                   TEXT,
    is_weekend                  INTEGER,        -- 0/1

    -- Severity
    accident_severity           INTEGER,        -- 1=Fatal 2=Serious 3=Slight
    severity_label              TEXT,
    is_fatal                    INTEGER,        -- 0/1
    is_serious                  INTEGER,        -- 0/1

    -- Counts
    number_of_casualties        INTEGER,
    number_of_vehicles          INTEGER,

    -- Geography
    police_force_label          TEXT,
    local_authority_district    TEXT,
    urban_rural_label           TEXT,
    latitude                    REAL,
    longitude                   REAL,

    -- Road characteristics
    speed_limit                 INTEGER,
    speed_limit_label           TEXT,
    road_type_label             TEXT,
    junction_label              TEXT,

    -- Conditions
    light_label                 TEXT,
    weather_label               TEXT,
    road_surface_label          TEXT,
    is_night                    INTEGER,        -- 0/1
    is_wet_road                 INTEGER,        -- 0/1

    -- Timestamps
    created_at                  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS casualties (
    -- Composite PK (accident_index + casualty_reference)
    accident_index              TEXT,
    casualty_reference          INTEGER,

    -- Severity
    casualty_severity           INTEGER,
    casualty_severity_label     TEXT,
    is_fatal                    INTEGER,
    is_serious                  INTEGER,

    -- Demographics
    age_of_casualty             INTEGER,
    age_band                    TEXT,
    sex_of_casualty             INTEGER,
    sex_label                   TEXT,

    -- Classification
    casualty_class              INTEGER,
    casualty_class_label        TEXT,           -- Driver/Passenger/Pedestrian

    -- Vehicle
    vehicle_type                INTEGER,
    vehicle_type_label          TEXT,

    PRIMARY KEY (accident_index, casualty_reference),
    FOREIGN KEY (accident_index) REFERENCES accidents(accident_index)
);

CREATE TABLE IF NOT EXISTS vehicles (
    accident_index              TEXT,
    vehicle_reference           INTEGER,

    -- Type
    vehicle_type                INTEGER,
    vehicle_type_label          TEXT,

    -- Engine & age
    engine_capacity_cc          INTEGER,
    engine_over_2000cc          INTEGER,
    vehicle_year_of_manufacture INTEGER,
    vehicle_age                 INTEGER,
    vehicle_age_band            TEXT,

    -- Driver
    age_of_driver               INTEGER,
    sex_of_driver               INTEGER,

    -- Impact
    vehicle_manoeuvre           INTEGER,
    first_point_of_impact       INTEGER,
    was_vehicle_left_hand_drive INTEGER,

    PRIMARY KEY (accident_index, vehicle_reference),
    FOREIGN KEY (accident_index) REFERENCES accidents(accident_index)
);


-- ── Dimension / lookup tables ─────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_date (
    date_key        TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year            INTEGER,
    quarter         INTEGER,
    month           INTEGER,
    month_name      TEXT,
    week_of_year    INTEGER,
    day_of_week     INTEGER,
    day_name        TEXT,
    is_weekend      INTEGER,
    is_bank_holiday INTEGER DEFAULT 0   -- can be updated manually
);

CREATE TABLE IF NOT EXISTS dim_police_force (
    force_code  INTEGER PRIMARY KEY,
    force_name  TEXT,
    region      TEXT
);

INSERT OR IGNORE INTO dim_police_force (force_code, force_name, region) VALUES
(1,  'Metropolitan Police',         'London'),
(3,  'Cumbria',                     'North West'),
(4,  'Lancashire',                  'North West'),
(5,  'Merseyside',                  'North West'),
(6,  'Greater Manchester',          'North West'),
(7,  'Cheshire',                    'North West'),
(10, 'Northumbria',                 'North East'),
(11, 'Durham',                      'North East'),
(12, 'North Yorkshire',             'Yorkshire & Humber'),
(13, 'West Yorkshire',              'Yorkshire & Humber'),
(14, 'South Yorkshire',             'Yorkshire & Humber'),
(16, 'Humberside',                  'Yorkshire & Humber'),
(17, 'Cleveland',                   'North East'),
(20, 'West Midlands',               'West Midlands'),
(21, 'Staffordshire',               'West Midlands'),
(22, 'West Mercia',                 'West Midlands'),
(23, 'Warwickshire',                'West Midlands'),
(25, 'Derbyshire',                  'East Midlands'),
(26, 'Nottinghamshire',             'East Midlands'),
(27, 'Lincolnshire',                'East Midlands'),
(28, 'Northamptonshire',            'East Midlands'),
(30, 'Leicestershire',              'East Midlands'),
(31, 'Cambridgeshire',              'East of England'),
(32, 'Norfolk',                     'East of England'),
(33, 'Suffolk',                     'East of England'),
(35, 'Hertfordshire',               'East of England'),
(36, 'Bedfordshire',                'East of England'),
(37, 'Thames Valley',               'South East'),
(40, 'Hampshire',                   'South East'),
(42, 'Sussex',                      'South East'),
(43, 'Surrey',                      'South East'),
(44, 'Kent',                        'South East'),
(45, 'Essex',                       'East of England'),
(46, 'City of London',              'London'),
(47, 'Avon and Somerset',           'South West'),
(48, 'Gloucestershire',             'South West'),
(49, 'Wiltshire',                   'South West'),
(50, 'Dorset',                      'South West'),
(52, 'Devon and Cornwall',          'South West'),
(53, 'Dyfed-Powys',                 'Wales'),
(54, 'Gwent',                       'Wales'),
(55, 'South Wales',                 'Wales'),
(56, 'North Wales',                 'Wales'),
(96, 'Police Scotland',             'Scotland');


-- ── Performance indexes ────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_acc_year           ON accidents(year);
CREATE INDEX IF NOT EXISTS idx_acc_severity       ON accidents(accident_severity);
CREATE INDEX IF NOT EXISTS idx_acc_date           ON accidents(accident_date);
CREATE INDEX IF NOT EXISTS idx_acc_police         ON accidents(police_force_label);
CREATE INDEX IF NOT EXISTS idx_acc_hour           ON accidents(hour);
CREATE INDEX IF NOT EXISTS idx_cas_accident       ON casualties(accident_index);
CREATE INDEX IF NOT EXISTS idx_cas_severity       ON casualties(casualty_severity);
CREATE INDEX IF NOT EXISTS idx_veh_accident       ON vehicles(accident_index);
CREATE INDEX IF NOT EXISTS idx_veh_type           ON vehicles(vehicle_type);

-- ── Confirmation ───────────────────────────────────────────────

SELECT 'Schema created successfully' AS status;
SELECT name, type FROM sqlite_master WHERE type IN ('table','index') ORDER BY type, name;
