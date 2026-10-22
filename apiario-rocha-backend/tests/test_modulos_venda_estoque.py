from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.main import app

client = TestClient(app)


def test_vendas_crud_routes(monkeypatch):
    async def fake_registrar_venda(payload):
        return {
            "_id": "venda_1",
            "codigo_venda": payload["codigo_venda"],
            "valor_bruto": payload["valor_bruto"],
            "tipo_venda": payload["tipo_venda"],
        }

    async def fake_listar_vendas():
        return [{"_id": "venda_1", "codigo_venda": "VEN-100", "valor_bruto": 250.0, "tipo_venda": "venda direta"}]

    async def fake_atualizar_venda(_id, payload):
        return {"_id": _id, **payload}

    async def fake_excluir_venda(_id):
        return {"_id": _id, "removido": True}

    monkeypatch.setattr("src.routes.vendas.registrar_venda", fake_registrar_venda)
    monkeypatch.setattr("src.routes.vendas.listar_vendas", fake_listar_vendas)
    monkeypatch.setattr("src.routes.vendas.atualizar_venda", fake_atualizar_venda)
    monkeypatch.setattr("src.routes.vendas.excluir_venda", fake_excluir_venda)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        create_response = client.post(
            "/api/v1/vendas/registrar",
            json={
                "codigo_venda": "VEN-100",
                "data_venda": "2026-10-21",
                "valor_bruto": 250.0,
                "tipo_venda": "venda direta",
            },
            headers={"Authorization": "Bearer test-token"},
        )
        list_response = client.get("/api/v1/vendas")
        update_response = client.put(
            "/api/v1/vendas/venda_1",
            json={"valor_bruto": 300.0, "tipo_venda": "venda direta"},
        )
        delete_response = client.delete("/api/v1/vendas/venda_1")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 200


def test_estoque_crud_routes(monkeypatch):
    async def fake_cadastrar_item(payload):
        return {"_id": "item_1", **payload}

    async def fake_listar_estoque():
        return [{"_id": "item_1", "produto": "Mel 1kg", "quantidade": 20, "preco_unitario": 25.5}]

    async def fake_atualizar_item(_id, payload):
        return {"_id": _id, **payload}

    async def fake_excluir_item(_id):
        return {"_id": _id, "removido": True}

    monkeypatch.setattr("src.routes.estoque.cadastrar_item_estoque", fake_cadastrar_item)
    monkeypatch.setattr("src.routes.estoque.listar_estoque", fake_listar_estoque)
    monkeypatch.setattr("src.routes.estoque.atualizar_item_estoque", fake_atualizar_item)
    monkeypatch.setattr("src.routes.estoque.excluir_item_estoque", fake_excluir_item)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        create_response = client.post(
            "/api/v1/estoque/cadastrar",
            json={
                "produto": "Mel 1kg",
                "quantidade": 20,
                "preco_unitario": 25.5,
                "categoria": "alimentos",
                "estoque_minimo": 5,
            },
            headers={"Authorization": "Bearer test-token"},
        )
        list_response = client.get("/api/v1/estoque")
        update_response = client.put(
            "/api/v1/estoque/item_1",
            json={"quantidade": 25, "preco_unitario": 26.0},
        )
        delete_response = client.delete("/api/v1/estoque/item_1")
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 200
