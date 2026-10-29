from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.usuario import AdministradorCreate, AdministradorUpdate
from src.services.cadastros_service import (
    atualizar_administrador,
    criar_administrador,
    excluir_administrador,
    listar_administradores,
)

router = APIRouter(prefix="/api/v1", tags=["administradores"])


@router.post("/administradores/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_administrador_route(payload: AdministradorCreate, usuario: str = Depends(get_current_user)):
    try:
        novo_admin = await criar_administrador(payload.model_dump())
        return {
            "message": "Administrador cadastrado com sucesso",
            "id_administrador": novo_admin.get("_id"),
            "nome": novo_admin["nome"],
            "email": novo_admin["email"],
            "username": novo_admin["username"],
            "nivel": novo_admin["nivel"],
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar administrador") from exc


@router.get("/administradores")
async def listar_administradores_route(usuario: str = Depends(get_current_user)):
    try:
        administradores = await listar_administradores()
        return {"usuario": usuario, "administradores": administradores}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar administradores") from exc


@router.put("/administradores/{administrador_id}")
async def atualizar_administrador_route(administrador_id: str, payload: AdministradorUpdate, usuario: str = Depends(get_current_user)):
    try:
        atualizado = await atualizar_administrador(administrador_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "administrador_atualizado": atualizado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar administrador") from exc


@router.delete("/administradores/{administrador_id}")
async def excluir_administrador_route(administrador_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_administrador(administrador_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir administrador") from exc
