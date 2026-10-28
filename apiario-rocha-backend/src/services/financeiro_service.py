from datetime import date, datetime, timezone
from decimal import Decimal
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
        "forma_pagamento": payload.get("forma_pagamento", "nao_informado"),
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


def _sale_as_movement(venda: dict[str, Any]) -> dict[str, Any]:
    codigo = venda.get("codigo_venda") or (venda.get("_id") or "")[:8]
    return {
        "_id": f"venda:{venda.get('_id', codigo)}",
        "tipo": "entrada",
        "descricao": f"Venda {codigo}",
        "categoria": "Vendas",
        "valor": float(venda.get("valor_bruto") or 0),
        "data_movimentacao": str(venda.get("data_venda") or "")[:10],
        "forma_pagamento": venda.get("forma_pagamento") or "nao_informado",
        "status": "realizada",
        "origem": "venda",
    }


def _venda_confirmada(venda: dict[str, Any]) -> bool:
    return str(venda.get("status") or "confirmada").lower() not in {
        "cancelada",
        "cancelado",
        "estornada",
    }


async def listar_movimentacoes_financeiras(
    data_inicio: str | None = None,
    data_fim: str | None = None,
    tipo: str | None = None,
) -> list[dict[str, Any]]:
    movimentacoes = await database.find_many(
        "movimentacoes_financeiras",
        order_by="data_movimentacao",
        descending=True,
    )
    vendas = await database.find_many("vendas", order_by="data_venda", descending=True)
    registros = [
        *movimentacoes,
        *(_sale_as_movement(venda) for venda in vendas if _venda_confirmada(venda)),
    ]

    if data_inicio:
        registros = [
            item for item in registros
            if str(item.get("data_movimentacao") or "")[:10] >= data_inicio
        ]
    if data_fim:
        registros = [
            item for item in registros
            if str(item.get("data_movimentacao") or "")[:10] <= data_fim
        ]
    if tipo:
        registros = [item for item in registros if item.get("tipo") == tipo]

    return sorted(
        registros,
        key=lambda item: (
            str(item.get("data_movimentacao") or ""),
            str(item.get("criado_em") or ""),
        ),
        reverse=True,
    )


async def registrar_movimentacao_financeira(payload: dict[str, Any]) -> dict[str, Any]:
    documento = {
        **payload,
        "valor": round(float(payload["valor"]), 2),
        "data_movimentacao": payload["data_movimentacao"].isoformat(),
        "criado_em": datetime.now(timezone.utc),
    }
    return await database.insert("movimentacoes_financeiras", documento)


async def atualizar_movimentacao_financeira(
    movimentacao_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    documento = {
        key: value.isoformat() if isinstance(value, date) else value
        for key, value in payload.items()
        if value is not None
    }
    if "valor" in documento:
        documento["valor"] = round(float(documento["valor"]), 2)
    if not documento:
        return await database.find_one(
            "movimentacoes_financeiras",
            {"_id": movimentacao_id},
        )

    updated = await database.update(
        "movimentacoes_financeiras",
        {"_id": movimentacao_id},
        documento,
    )
    if not updated:
        return None
    return await database.find_one("movimentacoes_financeiras", {"_id": movimentacao_id})


async def excluir_movimentacao_financeira(movimentacao_id: str) -> bool:
    return await database.delete(
        "movimentacoes_financeiras",
        {"_id": movimentacao_id},
    )


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def _resumo_periodo(
    inicio: date,
    fim: date,
    movimentacoes: list[dict[str, Any]],
    vendas: list[dict[str, Any]],
) -> dict[str, Any]:
    inicio_iso = inicio.isoformat()
    fim_iso = fim.isoformat()
    registros = [
        item for item in movimentacoes
        if inicio_iso <= str(item.get("data_movimentacao") or "")[:10] <= fim_iso
    ]
    vendas_periodo = [
        item for item in vendas
        if _venda_confirmada(item)
        and inicio_iso <= str(item.get("data_venda") or "")[:10] <= fim_iso
    ]
    entradas_realizadas = sum(
        (_decimal(item.get("valor")) for item in registros if item.get("tipo") == "entrada" and item.get("status") == "realizada"),
        Decimal("0"),
    ) + sum(
        (_decimal(item.get("valor_bruto")) for item in vendas_periodo),
        Decimal("0"),
    )
    saidas_realizadas = sum(
        (_decimal(item.get("valor")) for item in registros if item.get("tipo") == "saida" and item.get("status") == "realizada"),
        Decimal("0"),
    )
    entradas_pendentes = sum(
        (_decimal(item.get("valor")) for item in registros if item.get("tipo") == "entrada" and item.get("status") == "pendente"),
        Decimal("0"),
    )
    saidas_pendentes = sum(
        (_decimal(item.get("valor")) for item in registros if item.get("tipo") == "saida" and item.get("status") == "pendente"),
        Decimal("0"),
    )

    return {
        "data_inicio": inicio_iso,
        "data_fim": fim_iso,
        "entradas": round(float(entradas_realizadas), 2),
        "saidas": round(float(saidas_realizadas), 2),
        "saldo": round(float(entradas_realizadas - saidas_realizadas), 2),
        "entradas_pendentes": round(float(entradas_pendentes), 2),
        "saidas_pendentes": round(float(saidas_pendentes), 2),
        "quantidade_movimentacoes": len(registros) + len(vendas_periodo),
    }


async def obter_resumo_financeiro(data_referencia: date) -> dict[str, Any]:
    movimentacoes = await database.find_many("movimentacoes_financeiras")
    vendas = await database.find_many("vendas")
    primeiro_dia_mes = data_referencia.replace(day=1)
    primeiro_dia_ano = data_referencia.replace(month=1, day=1)
    hoje = date.today()

    resumo_atual = _resumo_periodo(date.min, min(hoje, date.max), movimentacoes, vendas)
    pendente_total = sum(
        (_decimal(item.get("valor")) for item in movimentacoes if item.get("status") == "pendente"),
        Decimal("0"),
    )
    return {
        "data_referencia": data_referencia.isoformat(),
        "saldo_atual": resumo_atual["saldo"],
        "total_pendente": round(float(pendente_total), 2),
        "dia": _resumo_periodo(data_referencia, data_referencia, movimentacoes, vendas),
        "mes": _resumo_periodo(primeiro_dia_mes, data_referencia, movimentacoes, vendas),
        "ano": _resumo_periodo(primeiro_dia_ano, data_referencia, movimentacoes, vendas),
    }


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
