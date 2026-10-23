from datetime import datetime, timezone
from typing import Any

from src.config.database import database


async def _baixa_estoque_automatica(produto: str | None, quantidade: int | None) -> None:
    if not produto or not quantidade or quantidade <= 0:
        return

    item_estoque = await database.find_one("estoque", {"produto": produto})
    if item_estoque is None:
        return

    nova_quantidade = max(0, int(item_estoque.get("quantidade", 0)) - int(quantidade))
    await database.update(
        "estoque",
        {"_id": item_estoque["_id"]},
        {
            "quantidade": nova_quantidade,
            "status": "disponivel" if nova_quantidade > 0 else "baixo",
            "atualizado_em": datetime.now(timezone.utc),
        },
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
    saved = await database.insert("vendas", documento)
    await _baixa_estoque_automatica(payload.get("produto"), payload.get("quantidade"))
    return saved


async def listar_vendas() -> list[dict[str, Any]]:
    return await database.find_many("vendas", order_by="data_venda", descending=True)


async def atualizar_venda(venda_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": venda_id, "updated": False}
    updated = await database.update("vendas", {"_id": venda_id}, document)
    venda = await database.find_one("vendas", {"_id": venda_id})
    return venda or {"_id": venda_id, "updated": updated}


async def excluir_venda(venda_id: str) -> dict[str, Any]:
    removed = await database.delete("vendas", {"_id": venda_id})
    return {"_id": venda_id, "removido": removed}


async def consultar_fundo_acumulado() -> dict[str, Any]:
    valor_acumulado = await database.sum("vendas", "valor_fundo")
    now = datetime.now(timezone.utc)
    return {
        "valor_acumulado": round(valor_acumulado, 2),
        "periodo": f"{now.year}-Q{(now.month - 1) // 3 + 1}",
        "updated_at": now.isoformat(),
    }


async def obter_resumo_operacional() -> dict[str, Any]:
    total_vendas = await database.count("vendas")
    total_clientes = await database.count("clientes")
    total_fornecedores = await database.count("fornecedores")
    total_funcionarios = await database.count("funcionarios")
    total_colmeias_ativas = await database.count("colmeias", {"status": "ativa"})
    total_lotes = await database.count("lotes")
    total_leituras_telemetria = await database.count("telemetria")
    fundo_acumulado = await database.sum("vendas", "valor_fundo")
    estoque_total = await database.sum("estoque", "quantidade")
    mes_atual = datetime.now(timezone.utc).strftime("%Y-%m")
    faturamento_mes = await database.sum("vendas", "valor_bruto", {"data_venda__startswith": mes_atual})

    return {
        "total_vendas": total_vendas,
        "fundo_acumulado": round(fundo_acumulado, 2),
        "total_funcionarios": total_funcionarios,
        "total_clientes": total_clientes,
        "total_fornecedores": total_fornecedores,
        "total_colmeias_ativas": total_colmeias_ativas,
        "total_lotes": total_lotes,
        "total_leituras_telemetria": total_leituras_telemetria,
        "estoque_total": int(estoque_total),
        "faturamento_mes": round(faturamento_mes, 2),
    }
