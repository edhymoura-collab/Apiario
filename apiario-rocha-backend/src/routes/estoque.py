from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.estoque import ItemEstoqueCreate, ItemEstoqueUpdate
from src.services.estoque_service import (
    atualizar_item_estoque,
    cadastrar_item_estoque,
    excluir_item_estoque,
    gerar_relatorio_estoque,
    listar_alertas_estoque,
    listar_estoque,
)

router = APIRouter(prefix="/api/v1", tags=["estoque"])


@router.post("/estoque/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_item_estoque_route(payload: ItemEstoqueCreate, usuario: str = Depends(get_current_user)):
    try:
        item = await cadastrar_item_estoque(payload.model_dump())
        return {
            "message": "Item de estoque cadastrado com sucesso",
            "id_item": item.get("_id"),
            "produto": item["produto"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
            "estoque_minimo": item["estoque_minimo"],
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar item de estoque") from exc


@router.get("/estoque")
async def listar_estoque_route(usuario: str = Depends(get_current_user)):
    try:
        itens = await listar_estoque()
        return {"usuario": usuario, "estoque": itens}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar estoque") from exc


@router.get("/estoque/alertas")
async def listar_alertas_estoque_route(usuario: str = Depends(get_current_user)):
    try:
        alertas = await listar_alertas_estoque()
        return {"usuario": usuario, "alertas": alertas}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar alertas de estoque") from exc


@router.get("/estoque/relatorio")
async def relatorio_estoque_route(usuario: str = Depends(get_current_user)):
    try:
        relatorio = await gerar_relatorio_estoque()
        return {"usuario": usuario, **relatorio}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao gerar relatório de estoque") from exc


@router.put("/estoque/{item_id}")
async def atualizar_item_estoque_route(item_id: str, payload: ItemEstoqueUpdate, usuario: str = Depends(get_current_user)):
    try:
        item = await atualizar_item_estoque(item_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "item_atualizado": item}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar item de estoque") from exc


@router.delete("/estoque/{item_id}")
async def excluir_item_estoque_route(item_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_item_estoque(item_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir item de estoque") from exc
