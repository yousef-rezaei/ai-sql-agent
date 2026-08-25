import pytest

from app.db.executor import (
    QueryExecutionError,
    execute_readonly_query,
)


def test_execute_safe_select():
    result = execute_readonly_query(
        """
        SELECT id, name, price
        FROM products
        ORDER BY id
        LIMIT 3
        """
    )

    assert result["row_count"] == 3

    assert result["columns"] == [
        "id",
        "name",
        "price",
    ]

    assert result["rows"][0]["name"] == "Laptop"


def test_database_user_cannot_delete():
    with pytest.raises(QueryExecutionError):
        execute_readonly_query(
            "DELETE FROM products;"
        )