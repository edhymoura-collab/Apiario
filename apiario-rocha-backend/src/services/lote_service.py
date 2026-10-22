from datetime import datetime, timezone
from typing import Any

from src.config.database import database


async def criar_lote(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "codigo_lote": payload["codigo_lote"],
        "variedade_florada": payload["variedade_florada"],
        "data_extracao": payload["data_extracao"],
        "umidade": payload["umidade"],
        "pureza": payload["pureza"],
        "quantidade_potes": payload["quantidade_potes"],
        "laboratorio": payload["laboratorio"],
        "storytelling": payload["storytelling"],
        "auditado": payload.get("auditado", True),
        "id_colmeia": payload.get("id_colmeia"),
        "criado_em": datetime.now(timezone.utc),
    }
    result = await database.lotes.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_lotes() -> list[dict[str, Any]]:
    cursor = database.lotes.find({}).sort("codigo_lote", 1)
    return [doc async for doc in cursor]


async def buscar_lote_por_codigo(codigo_lote: str) -> dict[str, Any] | None:
    return await database.lotes.find_one({"codigo_lote": codigo_lote})
