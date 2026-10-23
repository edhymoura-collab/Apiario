import asyncio

from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.config.database import database
from src.main import app
from src.services import financeiro_service


async def _populate_summary_database():
    rows = {
        "vendas": [
            {"valor_fundo": 75.0, "valor_bruto": 250.0, "data_venda": "2026-10-21"},
        ],
        "clientes": [{"nome": "Maria"}],
        "fornecedores": [{"nome": "Fornecedor"}],
        "funcionarios": [{"nome": "Ana"}],
        "colmeias": [{"codigo": "C-001", "status": "ativa"}],
        "lotes": [{"codigo_lote": "LOT-001"}],
        "telemetria": [{"id_colmeia": "C-001", "timestamp_utc": "2026-10-21T10:00:00+00:00"}],
        "estoque": [{"produto": "Mel", "quantidade": 18}],
    }
    for table, documents in rows.items():
        for document in documents:
            await database.insert(table, document)


def test_operational_summary_includes_apiary_metrics(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "dashboard.db")

    async def setup_and_summarize():
        await _populate_summary_database()
        return await financeiro_service.obter_resumo_operacional()

    summary = asyncio.run(setup_and_summarize())

    assert summary["total_colmeias_ativas"] == 1
    assert summary["total_lotes"] == 1
    assert summary["total_leituras_telemetria"] == 1
    assert summary["fundo_acumulado"] == 75.0
    assert summary["estoque_total"] == 18


def test_dashboard_summary_route_returns_apiary_metrics(monkeypatch):
    async def fake_obter_resumo_operacional():
        return {
            "total_colmeias_ativas": 6,
            "total_lotes": 9,
            "total_leituras_telemetria": 24,
        }

    monkeypatch.setattr("src.routes.financeiro.obter_resumo_operacional", fake_obter_resumo_operacional)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = TestClient(app).get("/api/v1/dashboard/resumo")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total_colmeias_ativas"] == 6
    assert response.json()["total_lotes"] == 9
    assert response.json()["total_leituras_telemetria"] == 24
