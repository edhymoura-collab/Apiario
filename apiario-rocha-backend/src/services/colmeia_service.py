from datetime import datetime, timezone
from typing import Any

from src.config.database import database


async def criar_colmeia(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "codigo": payload["codigo"],
        "nome": payload["nome"],
        "localizacao": payload["localizacao"],
        "status": payload.get("status", "ativa"),
        "observacoes": payload.get("observacoes"),
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.colmeias.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_colmeias() -> list[dict[str, Any]]:
    cursor = database.colmeias.find({}).sort("codigo", 1)
    return [doc async for doc in cursor]
