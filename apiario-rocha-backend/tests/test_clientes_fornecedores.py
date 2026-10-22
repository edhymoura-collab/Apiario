from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.main import app

client = TestClient(app)


def test_dashboard_resumo_route(monkeypatch):
    async def fake_resumo():
        return {
            "total_vendas": 5,
            "fundo_acumulado": 1200.5,
            "total_funcionarios": 3,
            "total_clientes": 8,
            "total_fornecedores": 4,
            "estoque_total": 42,
            "faturamento_mes": 750.0,
        }

    monkeypatch.setattr("src.routes.financeiro.obter_resumo_operacional", fake_resumo)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.get("/api/v1/dashboard/resumo", headers={"Authorization": "Bearer test-token"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_vendas"] == 5
    assert payload["fundo_acumulado"] == 1200.5
    assert payload["total_clientes"] == 8


def test_clientes_e_fornecedores_crud_routes(monkeypatch):
    async def fake_criar_cliente(payload):
        return {"_id": "cliente_1", **payload}

    async def fake_listar_clientes():
        return [{"_id": "cliente_1", "nome": "Maria", "email": "maria@email.com", "tipo": "pf"}]

    async def fake_atualizar_cliente(_id, payload):
        return {"_id": _id, **payload}

    async def fake_excluir_cliente(_id):
        return {"_id": _id, "removido": True}

    async def fake_criar_fornecedor(payload):
        return {"_id": "fornecedor_1", **payload}

    async def fake_listar_fornecedores():
        return [{"_id": "fornecedor_1", "nome": "Fornecedora A", "cnpj": "12.345.678/0001-99", "categoria": "insumos"}]

    async def fake_atualizar_fornecedor(_id, payload):
        return {"_id": _id, **payload}

    async def fake_excluir_fornecedor(_id):
        return {"_id": _id, "removido": True}

    monkeypatch.setattr("src.routes.clientes.criar_cliente", fake_criar_cliente)
    monkeypatch.setattr("src.routes.clientes.listar_clientes", fake_listar_clientes)
    monkeypatch.setattr("src.routes.clientes.atualizar_cliente", fake_atualizar_cliente)
    monkeypatch.setattr("src.routes.clientes.excluir_cliente", fake_excluir_cliente)

    monkeypatch.setattr("src.routes.fornecedores.criar_fornecedor", fake_criar_fornecedor)
    monkeypatch.setattr("src.routes.fornecedores.listar_fornecedores", fake_listar_fornecedores)
    monkeypatch.setattr("src.routes.fornecedores.atualizar_fornecedor", fake_atualizar_fornecedor)
    monkeypatch.setattr("src.routes.fornecedores.excluir_fornecedor", fake_excluir_fornecedor)

    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        clientes_post = client.post(
            "/api/v1/clientes/cadastrar",
            json={"nome": "Maria", "email": "maria@email.com", "tipo": "pf"},
            headers={"Authorization": "Bearer test-token"},
        )
        clientes_get = client.get("/api/v1/clientes")
        clientes_put = client.put("/api/v1/clientes/cliente_1", json={"nome": "Maria Souza"})
        clientes_delete = client.delete("/api/v1/clientes/cliente_1")

        fornecedores_post = client.post(
            "/api/v1/fornecedores/cadastrar",
            json={"nome": "Fornecedora A", "cnpj": "12.345.678/0001-99", "categoria": "insumos"},
            headers={"Authorization": "Bearer test-token"},
        )
        fornecedores_get = client.get("/api/v1/fornecedores")
        fornecedores_put = client.put("/api/v1/fornecedores/fornecedor_1", json={"nome": "Fornecedor B"})
        fornecedores_delete = client.delete("/api/v1/fornecedores/fornecedor_1")
    finally:
        app.dependency_overrides.clear()

    assert clientes_post.status_code == 201
    assert clientes_get.status_code == 200
    assert clientes_put.status_code == 200
    assert clientes_delete.status_code == 200

    assert fornecedores_post.status_code == 201
    assert fornecedores_get.status_code == 200
    assert fornecedores_put.status_code == 200
    assert fornecedores_delete.status_code == 200
