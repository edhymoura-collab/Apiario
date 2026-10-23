import asyncio

from src.config.database import database
from src.services.financeiro_service import registrar_venda


def test_registrar_venda_baixa_estoque_automaticamente(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "vendas.db")

    async def run_test():
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

    asyncio.run(run_test())
