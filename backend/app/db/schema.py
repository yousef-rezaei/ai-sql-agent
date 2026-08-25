
from sqlalchemy import inspect

from app.db.connection import engine


def get_database_schema() -> dict:
    inspector = inspect(engine)

    schema = {
        "tables": []
    }

    table_names = inspector.get_table_names(schema="public")

    for table_name in table_names:

        columns = inspector.get_columns(
            table_name,
            schema="public",
        )

        primary_key = inspector.get_pk_constraint(
            table_name,
            schema="public",
        )

        foreign_keys = inspector.get_foreign_keys(
            table_name,
            schema="public",
        )

        table_info = {
            "name": table_name,
            "columns": [],
            "primary_key": primary_key.get(
                "constrained_columns",
                [],
            ),
            "foreign_keys": [],
        }

        for column in columns:
            table_info["columns"].append(
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                }
            )

        for foreign_key in foreign_keys:
            table_info["foreign_keys"].append(
                {
                    "columns": foreign_key[
                        "constrained_columns"
                    ],
                    "referred_table": foreign_key[
                        "referred_table"
                    ],
                    "referred_columns": foreign_key[
                        "referred_columns"
                    ],
                }
            )

        schema["tables"].append(table_info)

    return schema


def get_schema_context() -> str:
    database_schema = get_database_schema()

    lines = []

    for table in database_schema["tables"]:

        lines.append(
            f"Table: {table['name']}"
        )

        primary_keys = set(
            table["primary_key"]
        )

        for column in table["columns"]:

            column_description = (
                f"- {column['name']}: "
                f"{column['type']}"
            )

            if column["name"] in primary_keys:
                column_description += " [PRIMARY KEY]"

            if not column["nullable"]:
                column_description += " [NOT NULL]"

            lines.append(column_description)

        for foreign_key in table["foreign_keys"]:

            local_columns = ", ".join(
                foreign_key["columns"]
            )

            referred_columns = ", ".join(
                foreign_key["referred_columns"]
            )

            lines.append(
                f"- FOREIGN KEY: "
                f"{local_columns} -> "
                f"{foreign_key['referred_table']}."
                f"{referred_columns}"
            )

        lines.append("")

    return "\n".join(lines)