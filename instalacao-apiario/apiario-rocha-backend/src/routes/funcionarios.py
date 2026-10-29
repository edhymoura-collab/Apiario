from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.usuario import FuncionarioCreate, FuncionarioUpdate
from src.services.cadastros_service import (
    atualizar_funcionario,
    criar_funcionario,
    excluir_funcionario,
    listar_funcionarios,
)

router = APIRouter(prefix="/api/v1", tags=["funcionarios"])


@router.post("/funcionarios/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_funcionario_route(payload: FuncionarioCreate, usuario: str = Depends(get_current_user)):
    try:
        novo_funcionario = await criar_funcionario(payload.model_dump())
        return {
            "message": "Funcionário cadastrado com sucesso",
            "id_funcionario": novo_funcionario.get("_id"),
            "nome": novo_funcionario["nome"],
            "email": novo_funcionario["email"],
            "cargo": novo_funcionario["cargo"],
            "departamento": novo_funcionario["departamento"],
            "salario": novo_funcionario["salario"],
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar funcionário") from exc


@router.get("/funcionarios")
async def listar_funcionarios_route(usuario: str = Depends(get_current_user)):
    try:
        funcionarios = await listar_funcionarios()
        return {"usuario": usuario, "funcionarios": funcionarios}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar funcionários") from exc


@router.put("/funcionarios/{funcionario_id}")
async def atualizar_funcionario_route(funcionario_id: str, payload: FuncionarioUpdate, usuario: str = Depends(get_current_user)):
    try:
        atualizado = await atualizar_funcionario(funcionario_id, payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "funcionario_atualizado": atualizado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar funcionário") from exc


@router.delete("/funcionarios/{funcionario_id}")
async def excluir_funcionario_route(funcionario_id: str, usuario: str = Depends(get_current_user)):
    try:
        resultado = await excluir_funcionario(funcionario_id)
        return {"usuario": usuario, "resultado": resultado}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir funcionário") from exc
