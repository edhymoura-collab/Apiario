from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.fornecedor import FornecedorCreate, FornecedorUpdate
from src.services.cadastros_service import (
    atualizar_fornecedor,
    criar_fornecedor,
    excluir_fornecedor,
    listar_fornecedores,
)

router = APIRouter(prefix="/api/v1", tags=["fornecedores"])


@router.post("/fornecedores/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_fornecedor_route(payload: FornecedorCreate, usuario: str = Depends(get_current_user)):
    try:
        fornecedor = await criar_fornecedor(payload.model_dump())
        return {
            "message": "Fornecedor cadastrado com sucesso",
            "id_fornecedor": fornecedor.get("_id"),
            "nome": fornecedor["nome"],
            "categoria": fornecedor.get("categoria"),
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar fornecedor") from exc


@router.get("/fornecedores")
async def listar_fornecedores_route(usuario: str = Depends(get_current_user)):
    try:
        fornecedores = await listar_fornecedores()
        return {"usuario": usuario, "fornecedores": fornecedores}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar fornecedores") from exc


@router.put("/fornecedores/{fornecedor_id}")
async def atualizar_fornecedor_route(fornecedor_id: str, payload: FornecedorUpdate, usuario: str = Depends(get_current_user)):
    try:
        fornecedor = await atualizar_fornecedor(fornecedor_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "fornecedor_atualizado": fornecedor}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar fornecedor") from exc


@router.delete("/fornecedores/{fornecedor_id}")
async def excluir_fornecedor_route(fornecedor_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_fornecedor(fornecedor_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir fornecedor") from exc
