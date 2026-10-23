from typing import Any

from src.config.database import database


async def buscar_lote_publico(codigo_lote: str) -> dict[str, Any] | None:
    lote = await database.find_one("lotes", {"codigo_lote": codigo_lote, "auditado": True})
    if lote is None:
        return None
    return {
        "codigo_lote": lote.get("codigo_lote"),
        "variedade_florada": lote.get("variedade_florada"),
        "data_extracao": lote.get("data_extracao"),
        "umidade": lote.get("umidade"),
        "pureza": lote.get("pureza"),
        "quantidade_potes": lote.get("quantidade_potes"),
        "laboratorio": lote.get("laboratorio"),
        "storytelling": lote.get("storytelling"),
    }
