from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.colmeia import ColmeiaCreate
from src.services.colmeia_service import criar_colmeia, listar_colmeias

router = APIRouter(prefix="/api/v1", tags=["colmeias"])


@router.post("/colmeias", status_code=status.HTTP_201_CREATED)
async def criar_colmeia_route(payload: ColmeiaCreate, usuario: str = Depends(get_current_user)):
    try:
        colmeia = await criar_colmeia(payload.model_dump())
        return {
            "id_colmeia": colmeia.get("_id"),
            "codigo": colmeia["codigo"],
            "nome": colmeia["nome"],
            "localizacao": colmeia["localizacao"],
            "status": colmeia["status"],
            "observacoes": colmeia.get("observacoes"),
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar colmeia") from exc


@router.get("/colmeias")
async def listar_colmeias_route(usuario: str = Depends(get_current_user)):
    try:
        colmeias = await listar_colmeias()
        return {"usuario": usuario, "colmeias": colmeias}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar colmeias") from exc
