from datetime import datetime, timezone
from typing import Any

from src.config.database import database


async def salvar_telemetria(payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    document = {
        "id_colmeia": payload["id_colmeia"],
        "timestamp_utc": payload["timestamp"],
        "peso_kg": payload["peso_kg"],
        "temperatura_c": payload["temperatura_c"],
        "umidade_p": payload["umidade_p"],
        "bateria_volt": payload.get("bateria_volt"),
        "criado_em": now,
    }
    result = await database.telemetria.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_historico_por_colmeia(id_colmeia: str) -> list[dict[str, Any]]:
    cursor = database.telemetria.find({"id_colmeia": id_colmeia}).sort("timestamp_utc", -1)
    return [doc async for doc in cursor]
