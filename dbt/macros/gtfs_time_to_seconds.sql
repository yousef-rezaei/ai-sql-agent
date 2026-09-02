{% macro gtfs_time_to_seconds(column_name) %}

CASE
    WHEN {{ column_name }}
         ~ '^[0-9]{1,3}:[0-5][0-9]:[0-5][0-9]$'

    THEN
          SPLIT_PART({{ column_name }}, ':', 1)::INTEGER * 3600
        + SPLIT_PART({{ column_name }}, ':', 2)::INTEGER * 60
        + SPLIT_PART({{ column_name }}, ':', 3)::INTEGER

    ELSE NULL
END

{% endmacro %}
