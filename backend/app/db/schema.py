from sqlalchemy import inspect

from app.db.connection import engine


QUERYABLE_SCHEMAS = (
    "public",
    "mobility",
)


SEMANTIC_RELATIONSHIPS = (
    {
        "from_table": "mobility.fact_trip",
        "from_column": "route_id",
        "to_table": "mobility.dim_route",
        "to_column": "route_id",
    },
    {
        "from_table": "mobility.fact_stop_time",
        "from_column": "trip_id",
        "to_table": "mobility.fact_trip",
        "to_column": "trip_id",
    },
    {
        "from_table": "mobility.fact_stop_time",
        "from_column": "station_id",
        "to_table": "mobility.dim_station",
        "to_column": "station_id",
    },
)


def get_database_schema() -> dict:
    inspector = inspect(engine)

    database_schema = {
        "tables": []
    }

    for schema_name in QUERYABLE_SCHEMAS:

        table_names = inspector.get_table_names(
            schema=schema_name
        )

        for table_name in sorted(table_names):

            columns = inspector.get_columns(
                table_name,
                schema=schema_name,
            )

            primary_key = inspector.get_pk_constraint(
                table_name,
                schema=schema_name,
            )

            foreign_keys = inspector.get_foreign_keys(
                table_name,
                schema=schema_name,
            )

            table_info = {
                "schema": schema_name,
                "name": table_name,
                "qualified_name": (
                    f"{schema_name}.{table_name}"
                ),
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

                referred_schema = (
                    foreign_key.get("referred_schema")
                    or schema_name
                )

                table_info["foreign_keys"].append(
                    {
                        "columns": foreign_key[
                            "constrained_columns"
                        ],
                        "referred_schema": referred_schema,
                        "referred_table": foreign_key[
                            "referred_table"
                        ],
                        "referred_columns": foreign_key[
                            "referred_columns"
                        ],
                    }
                )

            database_schema["tables"].append(
                table_info
            )

    return database_schema


def get_schema_context() -> str:
    database_schema = get_database_schema()

    lines = [
        (
            "Use schema-qualified table names exactly "
            "as shown below."
        ),
        "",
    ]

    for table in database_schema["tables"]:

        lines.append(
            f"Table: {table['qualified_name']}"
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
                f"{foreign_key['referred_schema']}."
                f"{foreign_key['referred_table']}."
                f"{referred_columns}"
            )

        lines.append("")

    lines.append("Known semantic relationships:")

    for relationship in SEMANTIC_RELATIONSHIPS:
        lines.append(
            "- "
            f"{relationship['from_table']}."
            f"{relationship['from_column']}"
            " -> "
            f"{relationship['to_table']}."
            f"{relationship['to_column']}"
        )

    return "\n".join(lines)