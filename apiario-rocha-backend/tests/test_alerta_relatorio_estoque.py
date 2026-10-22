from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.main import app

client = TestClient(app)


def test_alerta_e_relatorio_estoque(monkeypatch):
    async def fake_listar_estoque():
        return [
            {"_id": "item_1", "produto": "Mel", "quantidade": 2, "preco_unitario": 35.0, "estoque_minimo": 5},
            {"_id": "item_2", "produto": "Pote", "quantidade": 12, "preco_unitario": 10.0, "estoque_minimo": 3},
        ]

    async def fake_alertas_estoque():
        return [{"produto": "Mel", "quantidade": 2, "estoque_minimo": 5, "status": "baixo"}]

    async def fake_relatorio_estoque():
        return {"total_itens": 2, "total_quantidade": 14, "itens_em_alerta": 1, "valor_total_estoque": 470.0}

    monkeypatch.setattr("src.routes.estoque.listar_estoque", fake_listar_estoque)
    monkeypatch.setattr("src.routes.estoque.listar_alertas_estoque", fake_alertas_estoque)
    monkeypatch.setattr("src.routes.estoque.gerar_relatorio_estoque", fake_relatorio_estoque)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        alertas_response = client.get("/api/v1/estoque/alertas", headers={"Authorization": "Bearer token"})
        relatorio_response = client.get("/api/v1/estoque/relatorio", headers={"Authorization": "Bearer token"})
    finally:
        app.dependency_overrides.clear()

    assert alertas_response.status_code == 200
    assert relatorio_response.status_code == 200
    assert alertas_response.json()["alertas"][0]["produto"] == "Mel"
    assert relatorio_response.json()["itens_em_alerta"] == 1
