import asyncio

from src.config.database import database
from src.services.financeiro_service import registrar_venda


async def _run_valid_sale_test(db_path):
    original_path = database.path
    database.path = db_path
    try:
        await database.insert(
            "estoque",
            {
                "produto": "Leite",
                "quantidade": 10,
                "preco_unitario": 5.0,
                "estoque_minimo": 2,
                "unidade": "unidade",
                "status": "disponivel",
            },
        )
        result = await registrar_venda({
            "codigo_venda": "V-1001",
            "data_venda": "2026-10-21",
            "valor_bruto": 150.0,
            "tipo_venda": "venda",
            "produto": "Leite",
            "quantidade": 3,
        })
        estoque = await database.find_one("estoque", {"produto": "Leite"})

        assert result["codigo_venda"] == "V-1001"
        assert estoque["quantidade"] == 7
        assert estoque["status"] == "disponivel"
    finally:
        database.path = original_path


async def _run_stock_insufficient_test(db_path):
    original_path = database.path
    database.path = db_path
    try:
        await database.insert(
            "estoque",
            {
                "produto": "Leite",
                "quantidade": 10,
                "preco_unitario": 5.0,
                "estoque_minimo": 2,
                "unidade": "unidade",
                "status": "disponivel",
            },
        )
        try:
            await registrar_venda({
                "codigo_venda": "V-1002",
                "data_venda": "2026-10-21",
                "valor_bruto": 200.0,
                "tipo_venda": "venda",
                "produto": "Leite",
                "quantidade": 11,
            })
            assert False, "Esperava erro ao vender mais do que há em estoque"
        except ValueError as exc:
            assert "estoque" in str(exc).lower()

        vendas = await database.find_many("vendas")
        assert vendas == []
    finally:
        database.path = original_path


def test_registrar_venda_baixa_estoque_automaticamente(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "vendas.db")
    asyncio.run(_run_valid_sale_test(tmp_path / "vendas.db"))


def test_registrar_venda_rejeita_quantidade_maior_que_estoque(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "vendas_overflow.db")
    asyncio.run(_run_stock_insufficient_test(tmp_path / "vendas_overflow.db"))
