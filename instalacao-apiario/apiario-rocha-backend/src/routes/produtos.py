from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.produto import ProdutoCreate, ProdutoUpdate
from src.services.produto_service import (
    atualizar_produto,
    cadastrar_produto,
    excluir_produto,
    listar_produtos,
)

router = APIRouter(prefix="/api/v1", tags=["produtos"])


@router.post("/produtos/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_produto_route(payload: ProdutoCreate, usuario: str = Depends(get_current_user)):
    try:
        produto = await cadastrar_produto(payload.model_dump())
        return {
            "message": "Produto cadastrado com sucesso",
            "id_produto": produto.get("_id"),
            "produto": produto,
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar produto") from exc


@router.get("/produtos")
async def listar_produtos_route(usuario: str = Depends(get_current_user)):
    try:
        produtos = await listar_produtos()
        return {"usuario": usuario, "produtos": produtos}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar produtos") from exc


@router.put("/produtos/{produto_id}")
async def atualizar_produto_route(
    produto_id: str,
    payload: ProdutoUpdate,
    usuario: str = Depends(get_current_user),
):
    try:
        produto = await atualizar_produto(produto_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "produto_atualizado": produto}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar produto") from exc


@router.delete("/produtos/{produto_id}")
async def excluir_produto_route(produto_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_produto(produto_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir produto") from exc
