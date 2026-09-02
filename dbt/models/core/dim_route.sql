WITH source AS (

    SELECT *
    FROM {{ source('mobility_staging', 'routes') }}

)

SELECT
    BTRIM(route_id)
        AS route_id,

    NULLIF(BTRIM(agency_id), '')
        AS agency_id,

    NULLIF(BTRIM(route_short_name), '')
        AS route_short_name,

    NULLIF(BTRIM(route_long_name), '')
        AS route_long_name,

    NULLIF(BTRIM(route_type), '')::INTEGER
        AS route_type,

    NULLIF(BTRIM(route_color), '')
        AS route_color,

    NULLIF(BTRIM(route_text_color), '')
        AS route_text_color,

    NULLIF(BTRIM(route_desc), '')
        AS route_description

FROM source

WHERE route_id IS NOT NULL
  AND BTRIM(route_id) <> ''
