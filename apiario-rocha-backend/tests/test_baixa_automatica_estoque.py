import asyncio

from src.services.financeiro_service import registrar_venda


class FakeCollection:
    def __init__(self):
        self.docs = []

    async def insert_one(self, doc):
        self.docs.append(doc)
        return type("Result", (), {"inserted_id": "fake-id"})()

    async def find_one(self, query):
        if "produto" in query:
            return {"produto": "Leite", "quantidade": 10, "status": "disponivel"}
        return None

    async def update_one(self, query, update):
        self.last_update = {"query": query, "update": update}
        return None


class FakeDatabase:
    def __init__(self):
        self.vendas = FakeCollection()
        self.estoque = FakeCollection()


async def _run_test():
    fake_db = FakeDatabase()
    import src.services.financeiro_service as service

    original_db = service.database
    service.database = fake_db
    try:
        payload = {
            "codigo_venda": "V-1001",
            "data_venda": "2026-10-21",
            "valor_bruto": 150.0,
            "tipo_venda": "venda",
            "produto": "Leite",
            "quantidade": 3,
        }

        result = await registrar_venda(payload)
        assert result["codigo_venda"] == "V-1001"
        assert fake_db.estoque.last_update["update"]["$set"]["quantidade"] == 7
        assert fake_db.estoque.last_update["update"]["$set"]["status"] == "disponivel"
    finally:
        service.database = original_db


def test_registrar_venda_baixa_estoque_automaticamente():
    asyncio.run(_run_test())
