WITH source AS (

    SELECT *
    FROM {{ source('mobility_staging', 'trips') }}

)

SELECT
    BTRIM(trip_id)
        AS trip_id,

    BTRIM(route_id)
        AS route_id,

    NULLIF(BTRIM(service_id), '')
        AS service_id,

    NULLIF(BTRIM(trip_headsign), '')
        AS trip_headsign,

    NULLIF(BTRIM(trip_short_name), '')
        AS trip_short_name,

    NULLIF(BTRIM(direction_id), '')::SMALLINT
        AS direction_id,

    NULLIF(BTRIM(block_id), '')
        AS block_id,

    NULLIF(BTRIM(shape_id), '')
        AS shape_id,

    NULLIF(BTRIM(wheelchair_accessible), '')::SMALLINT
        AS wheelchair_accessible,

    NULLIF(BTRIM(bikes_allowed), '')::SMALLINT
        AS bikes_allowed

FROM source

WHERE trip_id IS NOT NULL
  AND BTRIM(trip_id) <> ''

  AND route_id IS NOT NULL
  AND BTRIM(route_id) <> ''
