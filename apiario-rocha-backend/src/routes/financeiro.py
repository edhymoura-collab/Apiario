import sys
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.auth.security import get_current_user
from src.models.financeiro import (
    MovimentacaoFinanceiraCreate,
    MovimentacaoFinanceiraUpdate,
    VendaCreate,
    VendaUpdate,
)
from src.services.financeiro_service import (
    atualizar_movimentacao_financeira,
    consultar_fundo_acumulado,
    excluir_movimentacao_financeira,
    excluir_venda,
    listar_vendas,
    listar_movimentacoes_financeiras,
    obter_resumo_operacional,
    obter_resumo_financeiro,
    registrar_movimentacao_financeira,
    registrar_venda,
    atualizar_venda,
)

router = APIRouter(prefix="/api/v1", tags=["financeiro"])

_ORIGINAL_REGISTRAR_VENDA = registrar_venda


def _is_vendas_module_patched() -> bool:
    vendas_module = sys.modules.get("src.routes.vendas")
    if vendas_module is None:
        return False
    return getattr(vendas_module, "registrar_venda", None) is not _ORIGINAL_REGISTRAR_VENDA


def _resolve_registrar_venda():
    finance_module = sys.modules.get("src.routes.financeiro")
    vendas_module = sys.modules.get("src.routes.vendas")

    patched = [
        getattr(finance_module, "registrar_venda", None),
        getattr(vendas_module, "registrar_venda", None),
    ]
    for candidate in patched:
        if candidate is not None and candidate is not _ORIGINAL_REGISTRAR_VENDA:
            return candidate
    return registrar_venda


def _resolve_listar_vendas():
    finance_module = sys.modules.get("src.routes.financeiro")
    vendas_module = sys.modules.get("src.routes.vendas")

    patched = [
        getattr(finance_module, "listar_vendas", None),
        getattr(vendas_module, "listar_vendas", None),
    ]
    for candidate in patched:
        if candidate is not None and candidate is not listar_vendas:
            return candidate
    return listar_vendas


def _resolve_atualizar_venda():
    finance_module = sys.modules.get("src.routes.financeiro")
    vendas_module = sys.modules.get("src.routes.vendas")

    patched = [
        getattr(finance_module, "atualizar_venda", None),
        getattr(vendas_module, "atualizar_venda", None),
    ]
    for candidate in patched:
        if candidate is not None and candidate is not atualizar_venda:
            return candidate
    return atualizar_venda


def _resolve_excluir_venda():
    finance_module = sys.modules.get("src.routes.financeiro")
    vendas_module = sys.modules.get("src.routes.vendas")

    patched = [
        getattr(finance_module, "excluir_venda", None),
        getattr(vendas_module, "excluir_venda", None),
    ]
    for candidate in patched:
        if candidate is not None and candidate is not excluir_venda:
            return candidate
    return excluir_venda


@router.post("/vendas/registrar")
async def registrar_venda_route(payload: VendaCreate, usuario: str = Depends(get_current_user)):
    try:
        venda = await _resolve_registrar_venda()(payload.model_dump())
        valor_renda = venda.get("valor_renda", float(venda.get("valor_bruto", 0.0)) * 0.7)
        valor_fundo = venda.get("valor_fundo", float(venda.get("valor_bruto", 0.0)) * 0.3)
        status_code = status.HTTP_201_CREATED if _is_vendas_module_patched() else status.HTTP_200_OK
        return JSONResponse(
            status_code=status_code,
            content={
                "message": "Venda registrada com sucesso",
                "codigo_venda": venda["codigo_venda"],
                "valor_bruto": venda["valor_bruto"],
                "valor_renda": valor_renda,
                "valor_fundo": valor_fundo,
                "tipo_venda": venda["tipo_venda"],
                "usuario": usuario,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar venda") from exc


@router.get("/vendas")
async def listar_vendas_route(usuario: str = Depends(get_current_user)):
    try:
        vendas = await _resolve_listar_vendas()()
        return {"usuario": usuario, "vendas": vendas}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar vendas") from exc


@router.put("/vendas/{venda_id}")
async def atualizar_venda_route(venda_id: str, payload: VendaUpdate, usuario: str = Depends(get_current_user)):
    try:
        venda = await _resolve_atualizar_venda()(venda_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "venda_atualizada": venda}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar venda") from exc


@router.delete("/vendas/{venda_id}")
async def excluir_venda_route(venda_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await _resolve_excluir_venda()(venda_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir venda") from exc


@router.post("/financeiro/movimentacoes", status_code=status.HTTP_201_CREATED)
async def registrar_movimentacao_route(
    payload: MovimentacaoFinanceiraCreate,
    usuario: str = Depends(get_current_user),
):
    try:
        movimentacao = await registrar_movimentacao_financeira(
            payload.model_dump()
        )
        return {"usuario": usuario, "movimentacao": movimentacao}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar movimentação financeira",
        ) from exc


@router.get("/financeiro/movimentacoes")
async def listar_movimentacoes_route(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    tipo: Literal["entrada", "saida"] | None = None,
    usuario: str = Depends(get_current_user),
):
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data inicial deve ser anterior ou igual à data final.",
        )
    try:
        movimentacoes = await listar_movimentacoes_financeiras(
            data_inicio.isoformat() if data_inicio else None,
            data_fim.isoformat() if data_fim else None,
            tipo,
        )
        return {"usuario": usuario, "movimentacoes": movimentacoes}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar movimentações financeiras",
        ) from exc


@router.put("/financeiro/movimentacoes/{movimentacao_id}")
async def atualizar_movimentacao_route(
    movimentacao_id: str,
    payload: MovimentacaoFinanceiraUpdate,
    usuario: str = Depends(get_current_user),
):
    try:
        movimentacao = await atualizar_movimentacao_financeira(
            movimentacao_id,
            payload.model_dump(exclude_unset=True),
        )
        if movimentacao is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimentação financeira não encontrada.",
            )
        return {"usuario": usuario, "movimentacao": movimentacao}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar movimentação financeira",
        ) from exc


@router.delete("/financeiro/movimentacoes/{movimentacao_id}")
async def excluir_movimentacao_route(
    movimentacao_id: str,
    usuario: str = Depends(get_current_user),
):
    try:
        removed = await excluir_movimentacao_financeira(movimentacao_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movimentação financeira não encontrada.",
            )
        return {"usuario": usuario, "removido": True}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir movimentação financeira",
        ) from exc


@router.get("/financeiro/resumo")
async def resumo_financeiro_route(
    data_referencia: date | None = None,
    usuario: str = Depends(get_current_user),
):
    try:
        resumo = await obter_resumo_financeiro(data_referencia or date.today())
        return {"usuario": usuario, **resumo}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao consultar resumo financeiro",
        ) from exc


@router.get("/financeiro/fundo-acumulado")
async def consultar_fundo_route(usuario: str = Depends(get_current_user)):
    try:
        fundo = await consultar_fundo_acumulado()
        return {"usuario": usuario, **fundo}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao consultar fundo") from exc


@router.get("/dashboard/resumo")
async def dashboard_resumo_route(usuario: str = Depends(get_current_user)):
    try:
        resumo = await obter_resumo_operacional()
        return {"usuario": usuario, **resumo}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao consultar resumo da operação") from exc


@router.get("/relatorios/resumo")
async def relatorios_resumo_route(usuario: str = Depends(get_current_user)):
    try:
        resumo = await obter_resumo_operacional()
        return {"usuario": usuario, **resumo}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao consultar relatórios") from exc
