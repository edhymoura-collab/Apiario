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
    return await database.insert("colmeias", document)


async def listar_colmeias() -> list[dict[str, Any]]:
    return await database.find_many("colmeias", order_by="codigo")
