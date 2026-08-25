from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "AI SQL Agent API is running"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_database_health_endpoint():
    response = client.get("/health/db")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert body["result"] == 1


def test_ai_query_endpoint(monkeypatch):

    fake_result = {
        "sql": (
            "SELECT name, price "
            "FROM products "
            "ORDER BY price DESC "
            "LIMIT 5"
        ),
        "purpose": (
            "Return the most expensive products."
        ),
        "answer": (
            "Laptop is the most expensive product."
        ),
        "columns": [
            "name",
            "price",
        ],
        "rows": [
            {
                "name": "Laptop",
                "price": 1200,
            }
        ],
        "row_count": 1,
        "attempt_count": 1,
    }

    def fake_run_sql_agent(question: str):
        return fake_result

    monkeypatch.setattr(
        "app.main.run_sql_agent",
        fake_run_sql_agent,
    )

    response = client.post(
        "/ai/query",
        json={
            "question":
                "What is the most expensive product?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert body["row_count"] == 1
    assert body["attempt_count"] == 1

    assert body["rows"][0]["name"] == "Laptop"



def test_ai_query_requires_question():
    response = client.post(
        "/ai/query",
        json={},
    )

    assert response.status_code == 422