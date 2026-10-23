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
    return await database.insert("telemetria", document)


async def listar_historico_por_colmeia(id_colmeia: str) -> list[dict[str, Any]]:
    return await database.find_many(
        "telemetria",
        {"id_colmeia": id_colmeia},
        order_by="timestamp_utc",
        descending=True,
    )
