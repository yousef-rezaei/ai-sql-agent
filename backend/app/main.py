from fastapi import FastAPI
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.schema import (
    get_database_schema,
    get_schema_context,
)
from app.db.executor import (
    QueryExecutionError,
    execute_readonly_query,
)
from app.security.sql_validator import validate_sql
from app.db.connection import engine
from app.ai.sql_agent import generate_sql
from app.models.query import QueryRequest

app = FastAPI(
    title="AI SQL Agent API",
    description="AI-powered natural-language to SQL API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI SQL Agent API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/health/db")
def database_health():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            )

            value = result.scalar_one()

        return {
            "status": "ok",
            "database": "connected",
            "result": value,
        }

    except SQLAlchemyError as exc:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }


@app.get("/debug/products")
def get_products():
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT
                        id,
                        name,
                        category,
                        price
                    FROM products
                    ORDER BY id
                    """
                )
            )

            products = [
                dict(row._mapping)
                for row in result
            ]

        return {
            "count": len(products),
            "data": products,
        }

    except SQLAlchemyError as exc:
        return {
            "status": "error",
            "detail": str(exc),
        }

@app.get("/schema")
def database_schema():
    return get_database_schema()


@app.get("/schema/context")
def schema_context():
    return {
        "schema": get_schema_context()
    }


@app.post("/ai/sql-preview")
def sql_preview(request: QueryRequest):

    try:

        result = generate_sql(
            request.question
        )

        return {
            "question": request.question,
            "status": "pending_validation",
            "sql": result["sql"],
            "purpose": result["purpose"],
        }

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )


@app.post("/ai/query")
def execute_ai_query(request: QueryRequest):

    try:
        generated = generate_sql(
            request.question
        )

        validation = validate_sql(
            generated["sql"]
        )

        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Generated SQL failed validation.",
                    "reason": validation.error,
                    "sql": generated["sql"],
                },
            )

        result = execute_readonly_query(
            validation.sql
        )

        return {
            "question": request.question,
            "status": "success",
            "sql": validation.sql,
            "purpose": generated["purpose"],
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
        }

    except QueryExecutionError as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Database query execution failed.",
                "reason": str(exc),
            },
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )