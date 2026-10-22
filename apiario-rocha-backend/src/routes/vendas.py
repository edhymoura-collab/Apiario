from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.financeiro import VendaCreate, VendaUpdate
from src.services.vendas_service import (
    consultar_fundo_acumulado,
    excluir_venda,
    listar_vendas,
    registrar_venda,
    atualizar_venda,
)

router = APIRouter(prefix="/api/v1", tags=["vendas"])


@router.post("/vendas/registrar", status_code=status.HTTP_201_CREATED)
async def registrar_venda_route(payload: VendaCreate, usuario: str = Depends(get_current_user)):
    try:
        venda = await registrar_venda(payload.model_dump())
        return {
            "message": "Venda registrada com sucesso",
            "codigo_venda": venda["codigo_venda"],
            "valor_bruto": venda["valor_bruto"],
            "valor_renda": venda["valor_renda"],
            "valor_fundo": venda["valor_fundo"],
            "tipo_venda": venda["tipo_venda"],
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar venda") from exc


@router.get("/vendas")
async def listar_vendas_route(usuario: str = Depends(get_current_user)):
    try:
        vendas = await listar_vendas()
        return {"usuario": usuario, "vendas": vendas}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar vendas") from exc


@router.put("/vendas/{venda_id}")
async def atualizar_venda_route(venda_id: str, payload: VendaUpdate, usuario: str = Depends(get_current_user)):
    try:
        venda = await atualizar_venda(venda_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "venda_atualizada": venda}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar venda") from exc


@router.delete("/vendas/{venda_id}")
async def excluir_venda_route(venda_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_venda(venda_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir venda") from exc


@router.get("/financeiro/fundo-acumulado")
async def consultar_fundo_route(usuario: str = Depends(get_current_user)):
    try:
        fundo = await consultar_fundo_acumulado()
        return {"usuario": usuario, **fundo}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao consultar fundo") from exc
