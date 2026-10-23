import asyncio

from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.config.database import SQLiteDatabase, database
from src.main import BASE_DIR, app


def test_sqlite_persists_customer_between_database_instances(tmp_path):
    database_path = tmp_path / "apiario.db"
    first_database = SQLiteDatabase(database_path)
    second_database = SQLiteDatabase(database_path)

    async def write_and_read():
        saved = await first_database.insert("clientes", {
            "nome": "Cliente persistente",
            "tipo": "pf",
        })
        loaded = await second_database.find_one("clientes", {"_id": saved["_id"]})
        return saved, loaded

    saved, loaded = asyncio.run(write_and_read())

    assert loaded is not None
    assert loaded["_id"] == saved["_id"]
    assert loaded["nome"] == "Cliente persistente"


def test_customer_api_crud_persists_in_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "apiario.db")
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/clientes/cadastrar",
                json={"nome": "Maria", "email": "maria@example.com", "tipo": "pf"},
            )
            customer_id = create_response.json()["id_cliente"]

            list_response = client.get("/api/v1/clientes")
            update_response = client.put(
                f"/api/v1/clientes/{customer_id}",
                json={"nome": "Maria Silva"},
            )
            updated_list_response = client.get("/api/v1/clientes")
            delete_response = client.delete(f"/api/v1/clientes/{customer_id}")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.json()["clientes"][0]["nome"] == "Maria"
    assert update_response.status_code == 200
    assert updated_list_response.json()["clientes"][0]["nome"] == "Maria Silva"
    assert delete_response.status_code == 200
    assert delete_response.json()["resultado"]["removido"] is True


def test_database_file_is_outside_public_backend_directory():
    assert not database.path.is_relative_to(BASE_DIR)


def test_static_routes_serve_only_frontend_assets():
    client = TestClient(app)

    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/script.js").status_code == 200
    assert client.get("/static/.env").status_code == 404
    assert client.get("/static/data/apiario.db").status_code == 404
