WITH source AS (

    SELECT *
    FROM {{ source('mobility_staging', 'stops') }}

),

cleaned AS (

    SELECT
        BTRIM(stop_id) AS station_id,

        NULLIF(BTRIM(stop_code), '')
            AS stop_code,

        BTRIM(stop_name)
            AS station_name,

        NULLIF(BTRIM(stop_desc), '')
            AS description,

        stop_lat::NUMERIC(9,6)
            AS latitude,

        stop_lon::NUMERIC(9,6)
            AS longitude,

        NULLIF(BTRIM(location_type), '')::SMALLINT
            AS location_type,

        NULLIF(BTRIM(parent_station), '')
            AS parent_station_id,

        NULLIF(BTRIM(wheelchair_boarding), '')::SMALLINT
            AS wheelchair_boarding,

        NULLIF(BTRIM(platform_code), '')
            AS platform_code

    FROM source

    WHERE stop_id IS NOT NULL
      AND BTRIM(stop_id) <> ''

      AND stop_name IS NOT NULL
      AND BTRIM(stop_name) <> ''

      AND stop_lat ~ '^-?[0-9]+(\.[0-9]+)?$'
      AND stop_lon ~ '^-?[0-9]+(\.[0-9]+)?$'

      AND stop_lat::NUMERIC BETWEEN -90 AND 90
      AND stop_lon::NUMERIC BETWEEN -180 AND 180

)

SELECT *
FROM cleaned
