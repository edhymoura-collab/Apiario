from __future__ import annotations

from typing import Any

from src.config.database import database

_EMPRESA_CACHE: dict[str, Any] = {}


def _normalize_empresa(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "razaoSocial": payload.get("razaoSocial") or payload.get("razao_social") or "",
        "nomeFantasia": payload.get("nomeFantasia") or payload.get("nome_fantasia") or "",
        "cnpj": payload.get("cnpj") or "",
        "inscricaoEstadual": payload.get("inscricaoEstadual") or payload.get("inscricao_estadual") or "",
        "endereco": payload.get("endereco") or "",
        "numero": payload.get("numero") or "",
        "complemento": payload.get("complemento") or "",
        "bairro": payload.get("bairro") or "",
        "cidade": payload.get("cidade") or "",
        "estado": payload.get("estado") or "",
        "cep": payload.get("cep") or "",
        "telefone": payload.get("telefone") or "",
        "email": payload.get("email") or "",
        "site": payload.get("site") or "",
        "segmento": payload.get("segmento") or "",
        "logoUrl": payload.get("logoUrl") or payload.get("logo_url") or "",
    }
    return {k: v for k, v in normalized.items() if v not in (None, "") or k == "logoUrl"}


def salvar_empresa(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_empresa(payload)
    _EMPRESA_CACHE.clear()
    _EMPRESA_CACHE.update(normalized)
    return dict(normalized)


async def salvar_empresa_async(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_empresa(payload)
    try:
        await database.empresa.delete_many({})
        await database.empresa.insert_one(normalized)
    except Exception:
        pass
    _EMPRESA_CACHE.clear()
    _EMPRESA_CACHE.update(normalized)
    return dict(normalized)


def obter_empresa() -> dict[str, Any]:
    return dict(_EMPRESA_CACHE)


async def obter_empresa_async() -> dict[str, Any]:
    try:
        empresa = await database.empresa.find_one({})
        if empresa:
            empresa = dict(empresa)
            if "_id" in empresa:
                empresa.pop("_id")
            return empresa
    except Exception:
        pass
    return dict(_EMPRESA_CACHE)
