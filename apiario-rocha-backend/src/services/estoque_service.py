from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from src.config.database import database


async def cadastrar_item_estoque(payload: dict[str, Any]) -> dict[str, Any]:
    item = {
        "produto": payload["produto"],
        "categoria": payload.get("categoria", "geral"),
        "quantidade": int(payload["quantidade"]),
        "preco_unitario": float(payload["preco_unitario"]),
        "estoque_minimo": int(payload.get("estoque_minimo", 0)),
        "unidade": payload.get("unidade", "unidade"),
        "status": "disponivel" if int(payload["quantidade"]) > 0 else "baixo",
        "criado_em": datetime.now(timezone.utc),
        "atualizado_em": datetime.now(timezone.utc),
    }
    result = await database.estoque.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return item


async def listar_estoque() -> list[dict[str, Any]]:
    cursor = database.estoque.find({}).sort("produto", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_item_estoque(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": item_id, "updated": False}
    if "quantidade" in document:
        document["quantidade"] = int(document["quantidade"])
        document["status"] = "disponivel" if document["quantidade"] > 0 else "baixo"
    if "preco_unitario" in document:
        document["preco_unitario"] = float(document["preco_unitario"])
    document["atualizado_em"] = datetime.now(timezone.utc)
    await database.estoque.update_one({"_id": ObjectId(item_id)}, {"$set": document})
    updated = await database.estoque.find_one({"_id": ObjectId(item_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_item_estoque(item_id: str) -> dict[str, Any]:
    result = await database.estoque.delete_one({"_id": ObjectId(item_id)})
    return {"_id": item_id, "removido": result.deleted_count > 0}


async def listar_alertas_estoque() -> list[dict[str, Any]]:
    itens = await listar_estoque()
    alertas: list[dict[str, Any]] = []

    for item in itens:
        quantidade = int(item.get("quantidade", 0) or 0)
        minimo = int(item.get("estoque_minimo", 0) or 0)
        if quantidade <= minimo or quantidade == 0:
            alertas.append({
                "produto": item.get("produto", "-"),
                "quantidade": quantidade,
                "estoque_minimo": minimo,
                "status": "baixo" if quantidade <= minimo else "zerado",
            })

    return alertas


async def gerar_relatorio_estoque() -> dict[str, Any]:
    itens = await listar_estoque()
    total_quantidade = sum(int(item.get("quantidade", 0) or 0) for item in itens)
    total_itens = len(itens)
    itens_alerta = await listar_alertas_estoque()
    valor_total = sum(
        float(item.get("preco_unitario", 0) or 0) * int(item.get("quantidade", 0) or 0)
        for item in itens
    )

    return {
        "total_itens": total_itens,
        "total_quantidade": total_quantidade,
        "itens_em_alerta": len(itens_alerta),
        "valor_total_estoque": round(valor_total, 2),
        "alertas": itens_alerta,
    }
