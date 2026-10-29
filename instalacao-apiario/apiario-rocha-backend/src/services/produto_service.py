from datetime import datetime, timezone
from typing import Any

from src.config.database import database


async def cadastrar_produto(payload: dict[str, Any]) -> dict[str, Any]:
    produto = {
        "nome": payload["nome"],
        "codigo": payload.get("codigo"),
        "categoria": payload.get("categoria", "geral"),
        "descricao": payload.get("descricao"),
        "preco": float(payload["preco"]),
        "unidade": payload.get("unidade", "unidade"),
        "ativo": payload.get("ativo", True),
        "data_cadastro": datetime.now(timezone.utc),
    }
    return await database.insert("produtos", produto)


async def listar_produtos() -> list[dict[str, Any]]:
    return await database.find_many("produtos", order_by="nome")


async def atualizar_produto(produto_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": produto_id, "updated": False}
    await database.update("produtos", {"_id": produto_id}, document)
    produto = await database.find_one("produtos", {"_id": produto_id})
    return produto or {"_id": produto_id, "updated": False}


async def excluir_produto(produto_id: str) -> dict[str, Any]:
    removed = await database.delete("produtos", {"_id": produto_id})
    return {"_id": produto_id, "removido": removed}
