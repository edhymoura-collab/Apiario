from fastapi import APIRouter, HTTPException, status

from src.services.rastreabilidade_service import buscar_lote_publico

router = APIRouter(prefix="/api/v1/rastreabilidade", tags=["rastreabilidade"])


@router.get("/{codigo_lote}")
async def consultar_lote_publico(codigo_lote: str):
    lote = await buscar_lote_publico(codigo_lote)
    if lote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote não encontrado")
    return lote
