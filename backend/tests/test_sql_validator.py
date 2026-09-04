import pytest

from app.security import sql_validator


@pytest.fixture
def allowed_tables(monkeypatch):
    tables = {
        "public.customers",
        "public.products",
        "public.orders",
        "public.order_items",
        "mobility.dim_station",
        "mobility.dim_route",
        "mobility.fact_trip",
        "mobility.fact_stop_time",
    }

    monkeypatch.setattr(
        sql_validator,
        "get_allowed_tables",
        lambda: tables,
    )

    return tables


def test_valid_select_query(allowed_tables):
    sql = """
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is True
    assert result.sql is not None
    assert result.error is None


def test_valid_mobility_query(allowed_tables):
    sql = """
    SELECT
        station_name,
        latitude,
        longitude
    FROM mobility.dim_station
    LIMIT 10;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is True


def test_valid_mobility_join(allowed_tables):
    sql = """
    SELECT
        r.route_short_name,
        COUNT(*) AS trip_count
    FROM mobility.fact_trip t
    JOIN mobility.dim_route r
        ON t.route_id = r.route_id
    GROUP BY r.route_short_name
    ORDER BY trip_count DESC
    LIMIT 10;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is True


def test_valid_cte_query(allowed_tables):
    sql = """
    WITH late_departures AS (
        SELECT
            station_id
        FROM mobility.fact_stop_time
        WHERE arrival_seconds >= 86400
    )
    SELECT
        station_id
    FROM late_departures
    LIMIT 10;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is True


def test_delete_is_rejected(allowed_tables):
    sql = "DELETE FROM products;"

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert result.error is not None


def test_drop_is_rejected(allowed_tables):
    sql = "DROP TABLE products;"

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False


def test_update_is_rejected(allowed_tables):
    sql = """
    UPDATE products
    SET price = 0;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False


def test_multiple_statements_are_rejected(
    allowed_tables,
):
    sql = """
    SELECT * FROM products;
    DELETE FROM products;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert result.error == (
        "Only one SQL statement is allowed."
    )


def test_unknown_table_is_rejected(
    allowed_tables,
):
    sql = """
    SELECT *
    FROM employee_salaries;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert "employee_salaries" in result.error


def test_staging_schema_is_rejected(
    allowed_tables,
):
    sql = """
    SELECT *
    FROM mobility_staging.stops;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert "mobility_staging.stops" in result.error


def test_wrong_schema_is_rejected(
    allowed_tables,
):
    sql = """
    SELECT *
    FROM secret.dim_station;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert "secret.dim_station" in result.error


def test_unqualified_mobility_table_is_rejected(
    allowed_tables,
):
    sql = """
    SELECT *
    FROM dim_station;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is False
    assert "public.dim_station" in result.error


def test_valid_join_query(
    allowed_tables,
):
    sql = """
    SELECT
        p.name,
        SUM(oi.quantity * p.price) AS revenue
    FROM products p
    JOIN order_items oi
        ON p.id = oi.product_id
    GROUP BY p.id, p.name
    ORDER BY revenue DESC
    LIMIT 5;
    """

    result = sql_validator.validate_sql(sql)

    assert result.is_valid is True