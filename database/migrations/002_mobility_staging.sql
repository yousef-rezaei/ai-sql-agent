CREATE SCHEMA IF NOT EXISTS mobility_staging;
CREATE SCHEMA IF NOT EXISTS mobility;


CREATE TABLE IF NOT EXISTS mobility_staging.stops (
    stop_id TEXT,
    stop_code TEXT,
    stop_name TEXT,
    stop_desc TEXT,
    stop_lat TEXT,
    stop_lon TEXT,
    location_type TEXT,
    parent_station TEXT,
    wheelchair_boarding TEXT,
    platform_code TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS mobility_staging.routes (
    route_id TEXT,
    agency_id TEXT,
    route_short_name TEXT,
    route_long_name TEXT,
    route_type TEXT,
    route_color TEXT,
    route_text_color TEXT,
    route_desc TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS mobility_staging.trips (
    route_id TEXT,
    service_id TEXT,
    trip_id TEXT,
    trip_headsign TEXT,
    trip_short_name TEXT,
    direction_id TEXT,
    block_id TEXT,
    shape_id TEXT,
    wheelchair_accessible TEXT,
    bikes_allowed TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS mobility_staging.stop_times (
    trip_id TEXT,
    stop_id TEXT,
    stop_sequence TEXT,
    pickup_type TEXT,
    drop_off_type TEXT,
    stop_headsign TEXT,
    arrival_time TEXT,
    departure_time TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
