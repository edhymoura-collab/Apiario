from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from src.config.database import database


async def criar_usuario(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "nome": payload["nome"],
        "email": payload["email"],
        "username": payload["username"],
        "password": payload["password"],
        "perfil": payload.get("perfil", "usuario"),
        "ativo": True,
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.usuarios.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_usuarios() -> list[dict[str, Any]]:
    cursor = database.usuarios.find({}).sort("nome", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_usuario(usuario_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": usuario_id, "updated": False}
    await database.usuarios.update_one({"_id": ObjectId(usuario_id)}, {"$set": document})
    updated = await database.usuarios.find_one({"_id": ObjectId(usuario_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_usuario(usuario_id: str) -> dict[str, Any]:
    result = await database.usuarios.delete_one({"_id": ObjectId(usuario_id)})
    return {"_id": usuario_id, "removido": result.deleted_count > 0}


async def criar_administrador(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "nome": payload["nome"],
        "email": payload["email"],
        "username": payload["username"],
        "password": payload["password"],
        "nivel": payload.get("nivel", "admin"),
        "ativo": True,
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.administradores.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_administradores() -> list[dict[str, Any]]:
    cursor = database.administradores.find({}).sort("nome", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_administrador(administrador_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": administrador_id, "updated": False}
    await database.administradores.update_one({"_id": ObjectId(administrador_id)}, {"$set": document})
    updated = await database.administradores.find_one({"_id": ObjectId(administrador_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_administrador(administrador_id: str) -> dict[str, Any]:
    result = await database.administradores.delete_one({"_id": ObjectId(administrador_id)})
    return {"_id": administrador_id, "removido": result.deleted_count > 0}


async def criar_funcionario(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "nome": payload["nome"],
        "email": payload["email"],
        "cargo": payload["cargo"],
        "departamento": payload["departamento"],
        "salario": float(payload["salario"]),
        "status": payload.get("status", "ativo"),
        "observacoes": payload.get("observacoes"),
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.funcionarios.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_funcionarios() -> list[dict[str, Any]]:
    cursor = database.funcionarios.find({}).sort("nome", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_funcionario(funcionario_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": funcionario_id, "updated": False}
    await database.funcionarios.update_one({"_id": ObjectId(funcionario_id)}, {"$set": document})
    updated = await database.funcionarios.find_one({"_id": ObjectId(funcionario_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_funcionario(funcionario_id: str) -> dict[str, Any]:
    result = await database.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
    return {"_id": funcionario_id, "removido": result.deleted_count > 0}


async def criar_cliente(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "nome": payload["nome"],
        "email": payload.get("email"),
        "telefone": payload.get("telefone"),
        "tipo": payload.get("tipo", "pf"),
        "documento": payload.get("documento"),
        "cidade": payload.get("cidade"),
        "observacoes": payload.get("observacoes"),
        "ativo": True,
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.clientes.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_clientes() -> list[dict[str, Any]]:
    cursor = database.clientes.find({}).sort("nome", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_cliente(cliente_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": cliente_id, "updated": False}
    await database.clientes.update_one({"_id": ObjectId(cliente_id)}, {"$set": document})
    updated = await database.clientes.find_one({"_id": ObjectId(cliente_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_cliente(cliente_id: str) -> dict[str, Any]:
    result = await database.clientes.delete_one({"_id": ObjectId(cliente_id)})
    return {"_id": cliente_id, "removido": result.deleted_count > 0}


async def criar_fornecedor(payload: dict[str, Any]) -> dict[str, Any]:
    document = {
        "nome": payload["nome"],
        "cnpj": payload.get("cnpj"),
        "email": payload.get("email"),
        "telefone": payload.get("telefone"),
        "categoria": payload.get("categoria", "geral"),
        "cidade": payload.get("cidade"),
        "observacoes": payload.get("observacoes"),
        "ativo": True,
        "data_cadastro": datetime.now(timezone.utc),
    }
    result = await database.fornecedores.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


async def listar_fornecedores() -> list[dict[str, Any]]:
    cursor = database.fornecedores.find({}).sort("nome", 1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_fornecedor(fornecedor_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": fornecedor_id, "updated": False}
    await database.fornecedores.update_one({"_id": ObjectId(fornecedor_id)}, {"$set": document})
    updated = await database.fornecedores.find_one({"_id": ObjectId(fornecedor_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_fornecedor(fornecedor_id: str) -> dict[str, Any]:
    result = await database.fornecedores.delete_one({"_id": ObjectId(fornecedor_id)})
    return {"_id": fornecedor_id, "removido": result.deleted_count > 0}


async def listar_vendas() -> list[dict[str, Any]]:
    cursor = database.vendas.find({}).sort("data_venda", -1)
    return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]


async def atualizar_venda(venda_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in payload.items() if value is not None}
    if not document:
        return {"_id": venda_id, "updated": False}
    await database.vendas.update_one({"_id": ObjectId(venda_id)}, {"$set": document})
    updated = await database.vendas.find_one({"_id": ObjectId(venda_id)})
    return {**updated, "_id": str(updated["_id"])}


async def excluir_venda(venda_id: str) -> dict[str, Any]:
    result = await database.vendas.delete_one({"_id": ObjectId(venda_id)})
    return {"_id": venda_id, "removido": result.deleted_count > 0}
