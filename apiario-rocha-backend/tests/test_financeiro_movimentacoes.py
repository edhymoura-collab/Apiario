import asyncio
import sqlite3

from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.config.database import database
from src.main import app


client = TestClient(app)


def test_legacy_sales_table_receives_payment_method_column(monkeypatch, tmp_path):
    database_path = tmp_path / "legacy-sales.db"
    monkeypatch.setattr(database, "path", database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE vendas ("_id" TEXT PRIMARY KEY, "codigo_venda" TEXT)')

    asyncio.run(database.find_many("vendas"))

    with sqlite3.connect(database_path) as connection:
        columns = {
            row[1] for row in connection.execute('PRAGMA table_info("vendas")')
        }
    assert "forma_pagamento" in columns


def test_financial_movement_crud(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "finance-crud.db")
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        create_response = client.post(
            "/api/v1/financeiro/movimentacoes",
            json={
                "tipo": "entrada",
                "descricao": "Venda de mel",
                "categoria": "Vendas",
                "valor": 125.5,
                "data_movimentacao": "2024-05-10",
                "forma_pagamento": "pix",
                "status": "realizada",
            },
        )
        movement_id = create_response.json()["movimentacao"]["_id"]
        list_response = client.get("/api/v1/financeiro/movimentacoes")
        update_response = client.put(
            f"/api/v1/financeiro/movimentacoes/{movement_id}",
            json={"valor": 150.25, "status": "pendente"},
        )
        invalid_response = client.post(
            "/api/v1/financeiro/movimentacoes",
            json={
                "tipo": "saida",
                "descricao": "Valor inválido",
                "categoria": "Teste",
                "valor": 0,
                "data_movimentacao": "2024-05-10",
                "forma_pagamento": "pix",
            },
        )
        delete_response = client.delete(
            f"/api/v1/financeiro/movimentacoes/{movement_id}"
        )
        missing_response = client.delete(
            f"/api/v1/financeiro/movimentacoes/{movement_id}"
        )
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert create_response.json()["movimentacao"]["valor"] == 125.5
    assert list_response.status_code == 200
    assert len(list_response.json()["movimentacoes"]) == 1
    assert update_response.status_code == 200
    assert update_response.json()["movimentacao"]["status"] == "pendente"
    assert invalid_response.status_code == 422
    assert delete_response.status_code == 200
    assert missing_response.status_code == 404


def test_financial_summary_counts_sales_once_and_excludes_pending(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "finance-summary.db")
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        database_rows = [
            {
                "tipo": "entrada",
                "descricao": "Venda avulsa",
                "categoria": "Outros",
                "valor": 100.0,
                "data_movimentacao": "2024-05-10",
                "forma_pagamento": "pix",
                "status": "realizada",
            },
            {
                "tipo": "saida",
                "descricao": "Compra de caixas",
                "categoria": "Materiais",
                "valor": 40.0,
                "data_movimentacao": "2024-05-10",
                "forma_pagamento": "dinheiro",
                "status": "realizada",
            },
            {
                "tipo": "entrada",
                "descricao": "Pagamento previsto",
                "categoria": "Outros",
                "valor": 20.0,
                "data_movimentacao": "2024-05-10",
                "forma_pagamento": "boleto",
                "status": "pendente",
            },
            {
                "tipo": "entrada",
                "descricao": "Receita anterior",
                "categoria": "Outros",
                "valor": 30.0,
                "data_movimentacao": "2024-04-30",
                "forma_pagamento": "pix",
                "status": "realizada",
            },
        ]

        async def seed_database():
            for row in database_rows:
                await database.insert("movimentacoes_financeiras", row)
            await database.insert(
                "vendas",
                {
                    "codigo_venda": "VEN-001",
                    "data_venda": "2024-05-10",
                    "valor_bruto": 50.0,
                    "valor_renda": 35.0,
                    "valor_fundo": 15.0,
                    "tipo_venda": "direta",
                    "forma_pagamento": "cartao_credito",
                    "status": "confirmada",
                },
            )

        asyncio.run(seed_database())
        response = client.get(
            "/api/v1/financeiro/resumo",
            params={"data_referencia": "2024-05-10"},
        )
        movement_response = client.get(
            "/api/v1/financeiro/movimentacoes",
            params={"data_inicio": "2024-05-10", "data_fim": "2024-05-10"},
        )
    finally:
        app.dependency_overrides.clear()

    summary = response.json()
    assert response.status_code == 200
    assert summary["saldo_atual"] == 140.0
    assert summary["total_pendente"] == 20.0
    assert summary["dia"]["entradas"] == 150.0
    assert summary["dia"]["saidas"] == 40.0
    assert summary["dia"]["saldo"] == 110.0
    assert summary["mes"]["saldo"] == 110.0
    assert summary["ano"]["entradas"] == 180.0
    assert summary["ano"]["saldo"] == 140.0
    assert len(movement_response.json()["movimentacoes"]) == 4
    assert any(
        item.get("origem") == "venda"
        for item in movement_response.json()["movimentacoes"]
    )
