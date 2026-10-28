from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.config.database import database
from src.models.usuario import UsuarioCreate, UsuarioUpdate
from src.services.cadastros_service import (
    atualizar_usuario,
    criar_usuario,
    excluir_usuario,
    listar_usuarios,
)

router = APIRouter(prefix="/api/v1", tags=["usuarios"])


async def _require_admin(username: str) -> None:
    if username == "admin":
        return

    usuario_db = await database.usuarios.find_one({"username": username})
    if not usuario_db or usuario_db.get("perfil") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")


@router.post("/usuarios/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario_route(payload: UsuarioCreate, usuario: str = Depends(get_current_user)):
    await _require_admin(usuario)
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
    await _require_admin(usuario)
    try:
        usuarios = await listar_usuarios()
        return {"usuario": usuario, "usuarios": usuarios}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar usuários") from exc


@router.put("/usuarios/{usuario_id}")
async def atualizar_usuario_route(usuario_id: str, payload: UsuarioUpdate, usuario: str = Depends(get_current_user)):
    await _require_admin(usuario)
    try:
        atualizado = await atualizar_usuario(usuario_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "usuario_atualizado": atualizado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar usuário") from exc


@router.delete("/usuarios/{usuario_id}")
async def excluir_usuario_route(usuario_id: str, usuario: str = Depends(get_current_user)):
    await _require_admin(usuario)
    try:
        resultado = await excluir_usuario(usuario_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir usuário") from exc
