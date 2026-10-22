from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from src.config.database import database


async def _baixa_estoque_automatica(produto: str | None, quantidade: int | None) -> None:
    if not produto or not quantidade or quantidade <= 0:
        return

    item_estoque = await database.estoque.find_one({"produto": produto})
    if item_estoque is None:
        return

    nova_quantidade = max(0, int(item_estoque.get("quantidade", 0)) - int(quantidade))
    novo_status = "disponivel" if nova_quantidade > 0 else "baixo"

    await database.estoque.update_one(
        {"produto": produto},
        {"$set": {"quantidade": nova_quantidade, "status": novo_status, "atualizado_em": datetime.now(timezone.utc)}},
    )


def calcular_divisao(valor_bruto: float) -> dict[str, float]:
    valor_renda = valor_bruto * 0.70
    valor_fundo = valor_bruto * 0.30
    return {
        "valor_renda": round(valor_renda, 2),
        "valor_fundo": round(valor_fundo, 2),
    }


async def registrar_venda(payload: dict[str, Any]) -> dict[str, Any]:
    divisao = calcular_divisao(payload["valor_bruto"])
    documento = {
        "codigo_venda": payload["codigo_venda"],
        "data_venda": payload["data_venda"],
        "valor_bruto": payload["valor_bruto"],
        "valor_renda": divisao["valor_renda"],
        "valor_fundo": divisao["valor_fundo"],
        "tipo_venda": payload["tipo_venda"],
        "produto": payload.get("produto"),
        "quantidade": int(payload["quantidade"]) if payload.get("quantidade") is not None else None,
        "status": "confirmada",
        "criado_em": datetime.now(timezone.utc),
    }
    await database.vendas.insert_one(documento)
    await _baixa_estoque_automatica(payload.get("produto"), payload.get("quantidade"))
    return documento


async def listar_vendas() -> list[dict[str, Any]]:
    cursor = database.vendas.find({}).sort("data_venda", -1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_venda(venda_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": venda_id, "updated": False}
    await database.vendas.update_one({"_id": ObjectId(venda_id)}, {"$set": document})
    updated = await database.vendas.find_one({"_id": ObjectId(venda_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_venda(venda_id: str) -> dict[str, Any]:
    result = await database.vendas.delete_one({"_id": ObjectId(venda_id)})
    return {"_id": venda_id, "removido": result.deleted_count > 0}


async def consultar_fundo_acumulado() -> dict[str, Any]:
    total = await database.vendas.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$valor_fundo"}}}
    ]).to_list(length=1)

    valor_acumulado = total[0]["total"] if total else 0.0
    return {
        "valor_acumulado": round(float(valor_acumulado), 2),
        "periodo": "2026-Q4",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


async def obter_resumo_operacional() -> dict[str, Any]:
    total_vendas = await database.vendas.count_documents({})
    total_clientes = await database.clientes.count_documents({})
    total_fornecedores = await database.fornecedores.count_documents({})
    total_funcionarios = await database.funcionarios.count_documents({})

    fundo_total = await database.vendas.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$valor_fundo"}}}
    ]).to_list(length=1)

    estoque_total = await database.estoque.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$quantidade"}}}
    ]).to_list(length=1)

    mes_atual = datetime.now(timezone.utc).strftime("%Y-%m")
    faturamento_mes = await database.vendas.aggregate([
        {"$match": {"data_venda": {"$regex": f"^{mes_atual}"}}},
        {"$group": {"_id": None, "total": {"$sum": "$valor_bruto"}}}
    ]).to_list(length=1)

    return {
        "total_vendas": total_vendas,
        "fundo_acumulado": round(float((fundo_total[0]["total"] if fundo_total else 0.0)), 2),
        "total_funcionarios": total_funcionarios,
        "total_clientes": total_clientes,
        "total_fornecedores": total_fornecedores,
        "estoque_total": int((estoque_total[0]["total"] if estoque_total else 0)),
        "faturamento_mes": round(float((faturamento_mes[0]["total"] if faturamento_mes else 0.0)), 2),
    }
