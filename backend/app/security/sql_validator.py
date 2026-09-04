from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from app.db.schema import get_database_schema


DEFAULT_SCHEMA = "public"


@dataclass
class ValidationResult:
    is_valid: bool
    sql: str | None = None
    error: str | None = None


def get_allowed_tables() -> set[str]:
    schema = get_database_schema()

    return {
        table["qualified_name"].lower()
        for table in schema["tables"]
    }


def get_referenced_tables(
    statement: exp.Expression,
) -> set[str]:

    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
        if cte.alias_or_name
    }

    referenced_tables = set()

    for table in statement.find_all(exp.Table):

        table_name = table.name.lower()

        # A CTE reference is not a physical DB table.
        if (
            not table.db
            and table_name in cte_names
        ):
            continue

        schema_name = (
            table.db.lower()
            if table.db
            else DEFAULT_SCHEMA
        )

        # PostgreSQL does not support normal
        # cross-database table access.
        if table.catalog:
            referenced_tables.add(
                (
                    f"{table.catalog.lower()}."
                    f"{schema_name}."
                    f"{table_name}"
                )
            )
            continue

        referenced_tables.add(
            f"{schema_name}.{table_name}"
        )

    return referenced_tables


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

    # Only one SQL statement is allowed.
    if len(statements) != 1:
        return ValidationResult(
            is_valid=False,
            error="Only one SQL statement is allowed.",
        )

    statement = statements[0]

    # SELECT / UNION / CTE query expressions only.
    if not isinstance(statement, exp.Query):
        return ValidationResult(
            is_valid=False,
            error=(
                "Only read-only SELECT queries "
                "are allowed."
            ),
        )

    allowed_tables = get_allowed_tables()

    referenced_tables = get_referenced_tables(
        statement
    )

    unknown_tables = (
        referenced_tables - allowed_tables
    )

    if unknown_tables:
        return ValidationResult(
            is_valid=False,
            error=(
                "Query references unknown or "
                "forbidden tables: "
                + ", ".join(
                    sorted(unknown_tables)
                )
            ),
        )

    normalized_sql = statement.sql(
        dialect="postgres"
    )

    return ValidationResult(
        is_valid=True,
        sql=normalized_sql,
    )