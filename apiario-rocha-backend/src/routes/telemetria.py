from fastapi import APIRouter, HTTPException, status

from src.models.telemetria import TelemetriaCreate, TelemetriaResponse
from src.services.telemetria_service import listar_historico_por_colmeia, salvar_telemetria

router = APIRouter(prefix="/api/v1/telemetria", tags=["telemetria"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def registrar_telemetria(payload: TelemetriaCreate):
    try:
        document = await salvar_telemetria(payload.model_dump())
        return {
            "message": "Leitura de telemetria registrada com sucesso",
            "data": {
                "id_colmeia": document["id_colmeia"],
                "timestamp_utc": document["timestamp_utc"],
                "peso_kg": document["peso_kg"],
                "temperatura_c": document["temperatura_c"],
                "umidade_p": document["umidade_p"],
                "bateria_volt": document.get("bateria_volt"),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar leitura de telemetria") from exc


@router.get("/{id_colmeia}")
async def consultar_historico(id_colmeia: str):
    historico = await listar_historico_por_colmeia(id_colmeia)
    return {"id_colmeia": id_colmeia, "historico": historico}
