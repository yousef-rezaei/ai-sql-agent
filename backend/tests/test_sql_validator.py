import pytest

from app.security import sql_validator


@pytest.fixture
def allowed_tables(monkeypatch):
    tables = {
        "customers",
        "products",
        "orders",
        "order_items",
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