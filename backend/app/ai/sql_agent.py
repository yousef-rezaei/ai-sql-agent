import json

from app.ai.client import get_openai_client
from app.core.config import settings
from app.db.executor import (
    QueryExecutionError,
    execute_readonly_query,
)
from app.db.schema import get_schema_context
from app.security.sql_validator import validate_sql


MAX_SQL_ATTEMPTS = 2


SQL_TOOL = {
    "type": "function",
    "name": "run_readonly_sql",
    "description": (
        "Validate and execute a safe read-only PostgreSQL query."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": (
                    "A PostgreSQL read-only SELECT query "
                    "using only the provided database schema."
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


class AgentExecutionError(Exception):
    pass


def build_instructions() -> str:
    schema_context = get_schema_context()

    return f"""
You are a PostgreSQL text-to-SQL agent.

Generate SQL using ONLY the database schema below.

Rules:
- Only generate read-only SELECT queries.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
  CREATE, TRUNCATE, GRANT, or REVOKE.
- Never invent tables or columns.
- Use schema-qualified table names exactly as provided in DATABASE SCHEMA.
- For mobility tables, always use the mobility schema prefix.
- Use the provided foreign-key relationships for joins.
- Prefer explicit column names instead of SELECT *.
- Add LIMIT 100 unless the query is an aggregate
  returning a small result.
- Use the run_readonly_sql tool whenever database access
  is required.

IMPORTANT ERROR RECOVERY RULE:
If run_readonly_sql returns an error:
1. Read the error carefully.
2. Inspect the database schema again.
3. Correct the SQL.
4. Call run_readonly_sql again.

After the tool succeeds:
Answer the user's original question using ONLY the tool result.
Keep the answer concise and factual.

DATABASE SCHEMA:

{schema_context}
"""


def find_sql_tool_call(response):
    for item in response.output:
        if (
            item.type == "function_call"
            and item.name == "run_readonly_sql"
        ):
            return item

    return None


def generate_sql(question: str) -> dict:
    """
    Generate SQL without executing it.
    Used by /ai/sql-preview.
    """

    client = get_openai_client()

    response = client.responses.create(
        model=settings.azure_openai_deployment,
        instructions=build_instructions(),
        input=question,
        tools=[SQL_TOOL],
    )

    tool_call = find_sql_tool_call(response)

    if tool_call is None:
        raise AgentExecutionError(
            "The model did not generate a SQL tool call."
        )

    arguments = json.loads(tool_call.arguments)

    return {
        "sql": arguments["sql"],
        "purpose": arguments["purpose"],
        "response_id": response.id,
        "call_id": tool_call.call_id,
    }


def run_sql_agent(question: str) -> dict:
    client = get_openai_client()

    instructions = build_instructions()

    response = client.responses.create(
        model=settings.azure_openai_deployment,
        instructions=instructions,
        input=question,
        tools=[SQL_TOOL],
    )

    last_error = None

    for attempt in range(1, MAX_SQL_ATTEMPTS + 1):

        tool_call = find_sql_tool_call(response)

        if tool_call is None:
            raise AgentExecutionError(
                "The model did not request SQL execution."
            )

        arguments = json.loads(tool_call.arguments)

        generated_sql = arguments["sql"]
        purpose = arguments["purpose"]

        # ----------------------------------
        # 1. Validate generated SQL
        # ----------------------------------

        validation = validate_sql(
            generated_sql
        )

        if not validation.is_valid:

            last_error = validation.error

            tool_output = {
                "ok": False,
                "stage": "validation",
                "sql": generated_sql,
                "error": validation.error,
            }

        else:

            # ----------------------------------
            # 2. Execute validated SQL
            # ----------------------------------

            try:
                result = execute_readonly_query(
                    validation.sql
                )

                tool_output = {
                    "ok": True,
                    "sql": validation.sql,
                    "columns": result["columns"],
                    "rows": result["rows"],
                    "row_count": result["row_count"],
                }

            except QueryExecutionError as exc:

                last_error = str(exc)

                tool_output = {
                    "ok": False,
                    "stage": "execution",
                    "sql": validation.sql,
                    "error": str(exc),
                }

        # ----------------------------------
        # 3. Return tool result to Azure
        # ----------------------------------

        next_response = client.responses.create(
            model=settings.azure_openai_deployment,
            previous_response_id=response.id,
            instructions=instructions,
            tools=[SQL_TOOL],
            input=[
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        tool_output,
                        default=str,
                    ),
                }
            ],
        )

        # ----------------------------------
        # SUCCESS
        # ----------------------------------

        if tool_output["ok"]:

            return {
                "sql": tool_output["sql"],
                "purpose": purpose,
                "columns": tool_output["columns"],
                "rows": tool_output["rows"],
                "row_count": tool_output["row_count"],
                "answer": next_response.output_text,
                "attempt_count": attempt,
            }

        # ----------------------------------
        # ERROR → let model repair SQL
        # ----------------------------------

        response = next_response

    raise AgentExecutionError(
        f"SQL execution failed after "
        f"{MAX_SQL_ATTEMPTS} attempts. "
        f"Last error: {last_error}"
    )