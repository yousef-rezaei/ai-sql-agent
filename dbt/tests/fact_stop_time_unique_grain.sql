SELECT
    trip_id,
    stop_sequence,
    COUNT(*) AS duplicate_count
FROM {{ ref('fact_stop_time') }}
GROUP BY
    trip_id,
    stop_sequence
HAVING COUNT(*) > 1