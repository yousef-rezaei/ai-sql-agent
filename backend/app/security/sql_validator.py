from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from app.db.schema import get_database_schema


@dataclass
class ValidationResult:
    is_valid: bool
    sql: str | None = None
    error: str | None = None


def get_allowed_tables() -> set[str]:
    schema = get_database_schema()

    return {
        table["name"].lower()
        for table in schema["tables"]
    }


def validate_sql(sql: str) -> ValidationResult:
    if not sql or not sql.strip():
        return ValidationResult(
            is_valid=False,
            error="SQL query is empty.",
        )

    try:
        statements = sqlglot.parse(
            sql,
            read="postgres",
        )
    except ParseError as exc:
        return ValidationResult(
            is_valid=False,
            error=f"Invalid SQL syntax: {exc}",
        )

    # Only one SQL statement is allowed
    if len(statements) != 1:
        return ValidationResult(
            is_valid=False,
            error="Only one SQL statement is allowed.",
        )

    statement = statements[0]

    # Only query expressions such as SELECT / UNION are allowed
    if not isinstance(statement, exp.Query):
        return ValidationResult(
            is_valid=False,
            error="Only read-only SELECT queries are allowed.",
        )

    allowed_tables = get_allowed_tables()

    referenced_tables = {
        table.name.lower()
        for table in statement.find_all(exp.Table)
    }

    unknown_tables = referenced_tables - allowed_tables

    if unknown_tables:
        return ValidationResult(
            is_valid=False,
            error=(
                "Query references unknown or forbidden tables: "
                + ", ".join(sorted(unknown_tables))
            ),
        )

    normalized_sql = statement.sql(
        dialect="postgres"
    )

    return ValidationResult(
        is_valid=True,
        sql=normalized_sql,
    )