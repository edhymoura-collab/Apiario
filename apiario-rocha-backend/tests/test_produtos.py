import asyncio

from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.config.database import SQLiteDatabase, database
from src.main import app
from src.services.sqlite_seed import seed_sample_data


client = TestClient(app)


def test_product_api_crud_persists_in_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "apiario.db")
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        with TestClient(app) as test_client:
            create_response = test_client.post(
                "/api/v1/produtos/cadastrar",
                json={
                    "codigo": "MEL-001",
                    "nome": "Mel silvestre 500g",
                    "categoria": "mel",
                    "descricao": "Pote de mel silvestre",
                    "preco": 35.5,
                    "unidade": "pote",
                },
            )
            product_id = create_response.json()["id_produto"]

            list_response = test_client.get("/api/v1/produtos")
            update_response = test_client.put(
                f"/api/v1/produtos/{product_id}",
                json={"preco": 37.0, "ativo": False},
            )
            updated_list_response = test_client.get("/api/v1/produtos")
            delete_response = test_client.delete(f"/api/v1/produtos/{product_id}")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.json()["produtos"][0]["nome"] == "Mel silvestre 500g"
    assert update_response.status_code == 200
    assert updated_list_response.json()["produtos"][0]["preco"] == 37.0
    assert updated_list_response.json()["produtos"][0]["ativo"] is False
    assert delete_response.status_code == 200
    assert delete_response.json()["resultado"]["removido"] is True


def test_product_rejects_negative_price():
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/produtos/cadastrar",
            json={"nome": "Mel", "preco": -1},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_products_table_is_created_for_existing_database(tmp_path):
    test_database = SQLiteDatabase(tmp_path / "apiario.db")

    async def create_and_read():
        saved = await test_database.insert("produtos", {
            "nome": "Mel",
            "preco": 20.0,
            "ativo": True,
        })
        return await test_database.find_one("produtos", {"_id": saved["_id"]})

    produto = asyncio.run(create_and_read())

    assert produto is not None
    assert produto["nome"] == "Mel"
    assert produto["ativo"] is True


def test_seed_sample_data_inserts_three_example_products(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "path", tmp_path / "apiario.db")

    async def seed_and_count():
        await seed_sample_data()
        return await database.count("produtos")

    count = asyncio.run(seed_and_count())

    assert count == 3


def test_seed_sample_data_populates_all_main_modules(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "path", tmp_path / "apiario.db")

    async def seed_all():
        await seed_sample_data()
        return {
            "empresa": await database.count("empresa"),
            "usuarios": await database.count("usuarios"),
            "administradores": await database.count("administradores"),
            "funcionarios": await database.count("funcionarios"),
            "clientes": await database.count("clientes"),
            "fornecedores": await database.count("fornecedores"),
            "colmeias": await database.count("colmeias"),
            "lotes": await database.count("lotes"),
            "produtos": await database.count("produtos"),
            "estoque": await database.count("estoque"),
            "vendas": await database.count("vendas"),
            "movimentacoes_financeiras": await database.count("movimentacoes_financeiras"),
            "telemetria": await database.count("telemetria"),
        }

    counts = asyncio.run(seed_all())

    for name, count in counts.items():
        assert count > 0, f"Módulo {name} não foi populado com exemplos"
