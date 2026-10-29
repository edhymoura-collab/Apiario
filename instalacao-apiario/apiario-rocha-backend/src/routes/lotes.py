from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.security import get_current_user
from src.models.lote import LoteCreate
from src.services.lote_service import buscar_lote_por_codigo, criar_lote, listar_lotes

router = APIRouter(prefix="/api/v1", tags=["lotes"])


@router.post("/lotes", status_code=status.HTTP_201_CREATED)
async def criar_lote_route(payload: LoteCreate, usuario: str = Depends(get_current_user)):
    try:
        lote = await criar_lote(payload.model_dump())
        return {
            "id_lote": lote.get("_id"),
            "codigo_lote": lote["codigo_lote"],
            "variedade_florada": lote["variedade_florada"],
            "data_extracao": lote["data_extracao"],
            "umidade": lote["umidade"],
            "pureza": lote["pureza"],
            "quantidade_potes": lote["quantidade_potes"],
            "laboratorio": lote["laboratorio"],
            "storytelling": lote["storytelling"],
            "auditado": lote.get("auditado", True),
            "usuario": usuario,
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar lote") from exc


@router.get("/lotes")
async def listar_lotes_route(usuario: str = Depends(get_current_user)):
    try:
        lotes = await listar_lotes()
        return {"usuario": usuario, "lotes": lotes}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar lotes") from exc


@router.get("/lotes/{codigo_lote}")
async def consultar_lote_interno(codigo_lote: str, usuario: str = Depends(get_current_user)):
    lote = await buscar_lote_por_codigo(codigo_lote)
    if lote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote não encontrado")
    return {"usuario": usuario, "lote": lote}
