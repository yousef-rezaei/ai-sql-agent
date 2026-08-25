from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.schema import (
    get_database_schema,
    get_schema_context,
)
from app.db.connection import engine


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

# @app.get("/schema/context")
# def schema_context():
#     return get_schema_context()
@app.get("/schema/context")
def schema_context():
    return {
        "schema": get_schema_context()
    }