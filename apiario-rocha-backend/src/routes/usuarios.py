from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.usuario import UsuarioCreate, UsuarioUpdate
from src.services.cadastros_service import (
    atualizar_usuario,
    criar_usuario,
    excluir_usuario,
    listar_usuarios,
)

router = APIRouter(prefix="/api/v1", tags=["usuarios"])


@router.post("/usuarios/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario_route(payload: UsuarioCreate, usuario: str = Depends(get_current_user)):
    try:
        novo_usuario = await criar_usuario(payload.model_dump())
        return {
            "message": "Usuário cadastrado com sucesso",
            "id_usuario": novo_usuario.get("_id"),
            "nome": novo_usuario["nome"],
            "email": novo_usuario["email"],
            "username": novo_usuario["username"],
            "perfil": novo_usuario["perfil"],
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar usuário") from exc


@router.get("/usuarios")
async def listar_usuarios_route(usuario: str = Depends(get_current_user)):
    try:
        usuarios = await listar_usuarios()
        return {"usuario": usuario, "usuarios": usuarios}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar usuários") from exc


@router.put("/usuarios/{usuario_id}")
async def atualizar_usuario_route(usuario_id: str, payload: UsuarioUpdate, usuario: str = Depends(get_current_user)):
    try:
        atualizado = await atualizar_usuario(usuario_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "usuario_atualizado": atualizado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar usuário") from exc


@router.delete("/usuarios/{usuario_id}")
async def excluir_usuario_route(usuario_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_usuario(usuario_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir usuário") from exc
