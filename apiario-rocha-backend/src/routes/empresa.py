from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.empresa import EmpresaProfile
from src.services.empresa_service import obter_empresa_async, salvar_empresa_async

router = APIRouter(prefix="/api/v1", tags=["empresa"])


@router.get("/empresa")
async def listar_empresa_route(usuario: str = Depends(get_current_user)):
    try:
        empresa = await obter_empresa_async()
        return {"usuario": usuario, "empresa": empresa}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao carregar dados da empresa") from exc


@router.put("/empresa")
async def salvar_empresa_route(payload: EmpresaProfile, usuario: str = Depends(get_current_user)):
    try:
        empresa = await salvar_empresa_async(payload.model_dump(exclude_none=True))
        return {"usuario": usuario, "empresa": empresa, "message": "Dados da empresa salvos com sucesso"}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao salvar dados da empresa") from exc
