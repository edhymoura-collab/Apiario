from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.cliente import ClienteCreate, ClienteUpdate
from src.services.cadastros_service import (
    atualizar_cliente,
    criar_cliente,
    excluir_cliente,
    listar_clientes,
)

router = APIRouter(prefix="/api/v1", tags=["clientes"])


@router.post("/clientes/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_cliente_route(payload: ClienteCreate, usuario: str = Depends(get_current_user)):
    try:
        cliente = await criar_cliente(payload.model_dump())
        return {
            "message": "Cliente cadastrado com sucesso",
            "id_cliente": cliente.get("_id"),
            "nome": cliente["nome"],
            "email": cliente.get("email"),
            "tipo": cliente.get("tipo", "pf"),
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar cliente") from exc


@router.get("/clientes")
async def listar_clientes_route(usuario: str = Depends(get_current_user)):
    try:
        clientes = await listar_clientes()
        return {"usuario": usuario, "clientes": clientes}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar clientes") from exc


@router.put("/clientes/{cliente_id}")
async def atualizar_cliente_route(cliente_id: str, payload: ClienteUpdate, usuario: str = Depends(get_current_user)):
    try:
        cliente = await atualizar_cliente(cliente_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "cliente_atualizado": cliente}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar cliente") from exc


@router.delete("/clientes/{cliente_id}")
async def excluir_cliente_route(cliente_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_cliente(cliente_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir cliente") from exc
