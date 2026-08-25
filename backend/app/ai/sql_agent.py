import json

from app.ai.client import get_openai_client
from app.core.config import settings
from app.db.schema import get_schema_context


SQL_TOOL = {
    "type": "function",
    "name": "run_readonly_sql",
    "description": (
        "Execute a safe read-only SQL query against the PostgreSQL database."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": (
                    "A PostgreSQL SELECT query generated "
                    "from the provided database schema."
                ),
            },
            "purpose": {
                "type": "string",
                "description": (
                    "A short explanation of what the query does."
                ),
            },
        },
        "required": [
            "sql",
            "purpose",
        ],
    },
}


def generate_sql(question: str) -> dict:

    client = get_openai_client()

    schema_context = get_schema_context()

    instructions = f"""
You are a PostgreSQL text-to-SQL agent.

You must generate SQL using ONLY the database schema provided below.

Rules:
- Only generate read-only SELECT queries.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or GRANT.
- Never invent tables or columns.
- Use the provided foreign-key relationships when joins are needed.
- Prefer explicit column names instead of SELECT *.
- Add LIMIT 100 unless the query is an aggregate returning a small result.
- When a database query is needed, call the run_readonly_sql tool.

DATABASE SCHEMA:

{schema_context}
"""

    response = client.responses.create(
        model=settings.azure_openai_deployment,
        instructions=instructions,
        input=question,
        tools=[SQL_TOOL],
    )

    for item in response.output:

        if (
            item.type == "function_call"
            and item.name == "run_readonly_sql"
        ):
            arguments = json.loads(item.arguments)

            return {
                "sql": arguments["sql"],
                "purpose": arguments["purpose"],
                "response_id": response.id,
            }

    raise RuntimeError(
        "The model did not generate a SQL tool call."
    )