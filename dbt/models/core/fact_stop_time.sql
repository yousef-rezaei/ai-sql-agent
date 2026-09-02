WITH source AS (

    SELECT *
    FROM {{ source('mobility_staging', 'stop_times') }}

)

SELECT
    BTRIM(trip_id)
        AS trip_id,

    BTRIM(stop_id)
        AS station_id,

    stop_sequence::INTEGER
        AS stop_sequence,

    NULLIF(BTRIM(arrival_time), '')
        AS arrival_time_gtfs,

    NULLIF(BTRIM(departure_time), '')
        AS departure_time_gtfs,

    {{ gtfs_time_to_seconds('arrival_time') }}
        AS arrival_seconds,

    {{ gtfs_time_to_seconds('departure_time') }}
        AS departure_seconds,

    NULLIF(BTRIM(pickup_type), '')::SMALLINT
        AS pickup_type,

    NULLIF(BTRIM(drop_off_type), '')::SMALLINT
        AS drop_off_type,

    NULLIF(BTRIM(stop_headsign), '')
        AS stop_headsign

FROM source

WHERE trip_id IS NOT NULL
  AND BTRIM(trip_id) <> ''

  AND stop_id IS NOT NULL
  AND BTRIM(stop_id) <> ''

  AND stop_sequence ~ '^[0-9]+$'
