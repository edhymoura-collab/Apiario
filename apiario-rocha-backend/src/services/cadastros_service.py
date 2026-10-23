from datetime import datetime, timezone
from typing import Any

from src.auth.passwords import hash_password
from src.config.database import database


async def _create(table: str, document: dict[str, Any]) -> dict[str, Any]:
    document["data_cadastro"] = datetime.now(timezone.utc)
    return await database.insert(table, document)


async def _list(table: str) -> list[dict[str, Any]]:
    records = await database.find_many(table, order_by="nome")
    if table in {"usuarios", "administradores"}:
        for record in records:
            record.pop("password", None)
    return records


async def _update(table: str, record_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": record_id, "updated": False}
    if table in {"usuarios", "administradores"} and "password" in document:
        document["password"] = hash_password(document["password"])
    updated = await database.update(table, {"_id": record_id}, document)
    record = await database.find_one(table, {"_id": record_id})
    if record and table in {"usuarios", "administradores"}:
        record.pop("password", None)
    return record or {"_id": record_id, "updated": updated}


async def _delete(table: str, record_id: str) -> dict[str, Any]:
    removed = await database.delete(table, {"_id": record_id})
    return {"_id": record_id, "removido": removed}


async def criar_usuario(payload: dict[str, Any]) -> dict[str, Any]:
    return await _create("usuarios", {
        "nome": payload["nome"],
        "email": payload["email"],
        "username": payload["username"],
        "password": hash_password(payload["password"]),
        "perfil": payload.get("perfil", "usuario"),
        "ativo": True,
    })


async def listar_usuarios() -> list[dict[str, Any]]:
    return await _list("usuarios")


async def atualizar_usuario(usuario_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("usuarios", usuario_id, payload)


async def excluir_usuario(usuario_id: str) -> dict[str, Any]:
    return await _delete("usuarios", usuario_id)


async def criar_administrador(payload: dict[str, Any]) -> dict[str, Any]:
    return await _create("administradores", {
        "nome": payload["nome"],
        "email": payload["email"],
        "username": payload["username"],
        "password": hash_password(payload["password"]),
        "nivel": payload.get("nivel", "admin"),
        "ativo": True,
    })


async def listar_administradores() -> list[dict[str, Any]]:
    return await _list("administradores")


async def atualizar_administrador(administrador_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("administradores", administrador_id, payload)


async def excluir_administrador(administrador_id: str) -> dict[str, Any]:
    return await _delete("administradores", administrador_id)


async def criar_funcionario(payload: dict[str, Any]) -> dict[str, Any]:
    return await _create("funcionarios", {
        "nome": payload["nome"],
        "email": payload["email"],
        "cargo": payload["cargo"],
        "departamento": payload["departamento"],
        "salario": float(payload["salario"]),
        "status": payload.get("status", "ativo"),
        "observacoes": payload.get("observacoes"),
        "ativo": True,
    })


async def listar_funcionarios() -> list[dict[str, Any]]:
    return await _list("funcionarios")


async def atualizar_funcionario(funcionario_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("funcionarios", funcionario_id, payload)


async def excluir_funcionario(funcionario_id: str) -> dict[str, Any]:
    return await _delete("funcionarios", funcionario_id)


async def criar_cliente(payload: dict[str, Any]) -> dict[str, Any]:
    return await _create("clientes", {
        "nome": payload["nome"],
        "email": payload.get("email"),
        "telefone": payload.get("telefone"),
        "tipo": payload.get("tipo", "pf"),
        "documento": payload.get("documento"),
        "cidade": payload.get("cidade"),
        "observacoes": payload.get("observacoes"),
        "ativo": True,
    })


async def listar_clientes() -> list[dict[str, Any]]:
    return await _list("clientes")


async def atualizar_cliente(cliente_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("clientes", cliente_id, payload)


async def excluir_cliente(cliente_id: str) -> dict[str, Any]:
    return await _delete("clientes", cliente_id)


async def criar_fornecedor(payload: dict[str, Any]) -> dict[str, Any]:
    return await _create("fornecedores", {
        "nome": payload["nome"],
        "cnpj": payload.get("cnpj"),
        "email": payload.get("email"),
        "telefone": payload.get("telefone"),
        "categoria": payload.get("categoria", "geral"),
        "cidade": payload.get("cidade"),
        "observacoes": payload.get("observacoes"),
        "ativo": True,
    })


async def listar_fornecedores() -> list[dict[str, Any]]:
    return await _list("fornecedores")


async def atualizar_fornecedor(fornecedor_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("fornecedores", fornecedor_id, payload)


async def excluir_fornecedor(fornecedor_id: str) -> dict[str, Any]:
    return await _delete("fornecedores", fornecedor_id)


async def listar_vendas() -> list[dict[str, Any]]:
    return await database.find_many("vendas", order_by="data_venda", descending=True)


async def atualizar_venda(venda_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return await _update("vendas", venda_id, payload)


async def excluir_venda(venda_id: str) -> dict[str, Any]:
    return await _delete("vendas", venda_id)
