from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.connection import engine


class QueryExecutionError(Exception):
    pass


def execute_readonly_query(sql: str) -> dict:
    try:
        with engine.begin() as connection:

            connection.execute(
                text("SET LOCAL statement_timeout = '5s'")
            )

            result = connection.execute(
                text(sql)
            )

            rows = [
                dict(row._mapping)
                for row in result
            ]

            columns = list(result.keys())

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
        }

    except SQLAlchemyError as exc:
        raise QueryExecutionError(
            str(exc)
        ) from exc