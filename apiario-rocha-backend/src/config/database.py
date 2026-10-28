import asyncio
import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

import aiosqlite

from src.auth.passwords import hash_password, is_password_hash
from src.config.settings import get_settings

settings = get_settings()

_TABLES = {
    "usuarios": {
        "nome": "TEXT",
        "email": "TEXT",
        "username": "TEXT",
        "password": "TEXT",
        "perfil": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "administradores": {
        "nome": "TEXT",
        "email": "TEXT",
        "username": "TEXT",
        "password": "TEXT",
        "nivel": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "funcionarios": {
        "nome": "TEXT",
        "email": "TEXT",
        "cargo": "TEXT",
        "departamento": "TEXT",
        "salario": "REAL",
        "status": "TEXT",
        "observacoes": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "clientes": {
        "nome": "TEXT",
        "email": "TEXT",
        "telefone": "TEXT",
        "tipo": "TEXT",
        "documento": "TEXT",
        "cidade": "TEXT",
        "observacoes": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "fornecedores": {
        "nome": "TEXT",
        "cnpj": "TEXT",
        "email": "TEXT",
        "telefone": "TEXT",
        "categoria": "TEXT",
        "cidade": "TEXT",
        "observacoes": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "vendas": {
        "codigo_venda": "TEXT",
        "data_venda": "TEXT",
        "valor_bruto": "REAL",
        "valor_renda": "REAL",
        "valor_fundo": "REAL",
        "tipo_venda": "TEXT",
        "forma_pagamento": "TEXT",
        "produto": "TEXT",
        "quantidade": "INTEGER",
        "status": "TEXT",
        "criado_em": "TEXT",
    },
    "movimentacoes_financeiras": {
        "tipo": "TEXT",
        "descricao": "TEXT",
        "categoria": "TEXT",
        "valor": "REAL",
        "data_movimentacao": "TEXT",
        "forma_pagamento": "TEXT",
        "status": "TEXT",
        "criado_em": "TEXT",
    },
    "estoque": {
        "produto": "TEXT",
        "categoria": "TEXT",
        "quantidade": "INTEGER",
        "preco_unitario": "REAL",
        "estoque_minimo": "INTEGER",
        "unidade": "TEXT",
        "status": "TEXT",
        "criado_em": "TEXT",
        "atualizado_em": "TEXT",
    },
    "produtos": {
        "nome": "TEXT",
        "codigo": "TEXT",
        "categoria": "TEXT",
        "descricao": "TEXT",
        "preco": "REAL",
        "unidade": "TEXT",
        "ativo": "INTEGER",
        "data_cadastro": "TEXT",
    },
    "colmeias": {
        "codigo": "TEXT",
        "nome": "TEXT",
        "localizacao": "TEXT",
        "status": "TEXT",
        "observacoes": "TEXT",
        "data_cadastro": "TEXT",
    },
    "lotes": {
        "codigo_lote": "TEXT",
        "variedade_florada": "TEXT",
        "data_extracao": "TEXT",
        "umidade": "REAL",
        "pureza": "REAL",
        "quantidade_potes": "INTEGER",
        "laboratorio": "TEXT",
        "storytelling": "TEXT",
        "auditado": "INTEGER",
        "id_colmeia": "TEXT",
        "criado_em": "TEXT",
    },
    "telemetria": {
        "id_colmeia": "TEXT",
        "timestamp_utc": "TEXT",
        "peso_kg": "REAL",
        "temperatura_c": "REAL",
        "umidade_p": "REAL",
        "bateria_volt": "REAL",
        "criado_em": "TEXT",
    },
    "empresa": {
        "razaoSocial": "TEXT",
        "nomeFantasia": "TEXT",
        "cnpj": "TEXT",
        "inscricaoEstadual": "TEXT",
        "endereco": "TEXT",
        "numero": "TEXT",
        "complemento": "TEXT",
        "bairro": "TEXT",
        "cidade": "TEXT",
        "estado": "TEXT",
        "cep": "TEXT",
        "telefone": "TEXT",
        "email": "TEXT",
        "site": "TEXT",
        "segmento": "TEXT",
        "logoUrl": "TEXT",
    },
}
_BOOLEAN_FIELDS = {"ativo", "auditado"}


def _database_path() -> Path:
    configured_path = Path(settings.sqlite_path).expanduser()
    if not configured_path.is_absolute():
        configured_path = Path(__file__).resolve().parents[2] / configured_path
    return configured_path.resolve()


class SQLiteDatabase:
    def __init__(self, path: Path):
        self.path = path

    async def _connect(self) -> aiosqlite.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = await aiosqlite.connect(self.path, timeout=5)
        try:
            connection.row_factory = aiosqlite.Row
            await connection.execute("PRAGMA foreign_keys = ON")
            await connection.execute("PRAGMA busy_timeout = 5000")
            await self._create_tables(connection)
            return connection
        except Exception:
            await connection.close()
            raise

    async def _create_tables(self, connection: aiosqlite.Connection) -> None:
        for table_name, columns in _TABLES.items():
            column_definitions = [
                '"_id" TEXT PRIMARY KEY',
                *(f'"{column}" {data_type}' for column, data_type in columns.items()),
            ]
            await connection.execute(
                f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_definitions)})'
            )
            cursor = await connection.execute(f'PRAGMA table_info("{table_name}")')
            existing_columns = {row["name"] for row in await cursor.fetchall()}
            for column, data_type in columns.items():
                if column not in existing_columns:
                    await connection.execute(
                        f'ALTER TABLE "{table_name}" ADD COLUMN "{column}" {data_type}'
                    )
        await connection.execute(
            'CREATE INDEX IF NOT EXISTS "idx_telemetria_colmeia_timestamp" '
            'ON "telemetria" ("id_colmeia", "timestamp_utc")'
        )
        await connection.commit()

    def _validate_table(self, table: str) -> None:
        if table not in _TABLES:
            raise ValueError(f"Tabela não permitida: {table}")

    def _validate_field(self, table: str, field: str) -> None:
        self._validate_table(table)
        if field != "_id" and field not in _TABLES[table]:
            raise ValueError(f"Campo não permitido para {table}: {field}")

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, bool):
            return int(value)
        return value

    @staticmethod
    def _document(row: aiosqlite.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        document = dict(row)
        for field in _BOOLEAN_FIELDS.intersection(document):
            if document[field] is not None:
                document[field] = bool(document[field])
        return document

    async def initialize(self) -> None:
        connection = await self._connect()
        try:
            await self._migrate_plaintext_passwords(connection)
            await connection.commit()
        finally:
            await connection.close()

    @staticmethod
    async def _migrate_plaintext_passwords(connection: aiosqlite.Connection) -> None:
        for table_name in ("usuarios", "administradores"):
            cursor = await connection.execute(f'SELECT "_id", "password" FROM "{table_name}"')
            for row in await cursor.fetchall():
                stored_password = row["password"]
                if stored_password and not is_password_hash(stored_password):
                    await connection.execute(
                        f'UPDATE "{table_name}" SET "password" = ? WHERE "_id" = ?',
                        (hash_password(stored_password), row["_id"]),
                    )

    async def command(self, command: str) -> dict[str, int]:
        if command != "ping":
            raise ValueError(f"Comando SQLite desconhecido: {command}")
        connection = await self._connect()
        try:
            await connection.execute("SELECT 1")
        finally:
            await connection.close()
        return {"ok": 1}

    async def insert(self, table: str, document: dict[str, Any]) -> dict[str, Any]:
        self._validate_table(table)
        saved = dict(document)
        saved.setdefault("_id", uuid.uuid4().hex)
        fields = list(saved)
        for field in fields:
            self._validate_field(table, field)
        values = [self._serialize(saved[field]) for field in fields]
        placeholders = ", ".join("?" for _ in fields)
        columns = ", ".join(f'"{field}"' for field in fields)
        connection = await self._connect()
        try:
            await connection.execute(
                f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})',
                values,
            )
            await connection.commit()
        finally:
            await connection.close()
        return saved

    async def upsert(self, table: str, document: dict[str, Any]) -> dict[str, Any]:
        self._validate_table(table)
        saved = dict(document)
        saved.setdefault("_id", uuid.uuid4().hex)
        fields = list(saved)
        for field in fields:
            self._validate_field(table, field)
        values = [self._serialize(saved[field]) for field in fields]
        placeholders = ", ".join("?" for _ in fields)
        columns = ", ".join(f'"{field}"' for field in fields)
        updates = ", ".join(f'"{field}" = excluded."{field}"' for field in fields if field != "_id")
        connection = await self._connect()
        try:
            await connection.execute(
                f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) '
                f'ON CONFLICT("_id") DO UPDATE SET {updates}',
                values,
            )
            await connection.commit()
        finally:
            await connection.close()
        return saved

    def _where_clause(self, table: str, filters: dict[str, Any]) -> tuple[str, list[Any]]:
        self._validate_table(table)
        conditions = []
        values = []
        for field, value in filters.items():
            if field.endswith("__startswith"):
                field = field.removesuffix("__startswith")
                self._validate_field(table, field)
                conditions.append(f'"{field}" LIKE ?')
                values.append(f"{self._serialize(value)}%")
                continue
            self._validate_field(table, field)
            if value is None:
                conditions.append(f'"{field}" IS NULL')
            else:
                conditions.append(f'"{field}" = ?')
                values.append(self._serialize(value))
        return (" WHERE " + " AND ".join(conditions) if conditions else ""), values

    async def find_one(self, table: str, filters: dict[str, Any]) -> dict[str, Any] | None:
        where, values = self._where_clause(table, filters)
        connection = await self._connect()
        try:
            cursor = await connection.execute(f'SELECT * FROM "{table}"{where} LIMIT 1', values)
            return self._document(await cursor.fetchone())
        finally:
            await connection.close()

    async def find_many(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[dict[str, Any]]:
        where, values = self._where_clause(table, filters or {})
        ordering = ""
        if order_by:
            self._validate_field(table, order_by)
            ordering = f' ORDER BY "{order_by}" {"DESC" if descending else "ASC"}'
        connection = await self._connect()
        try:
            cursor = await connection.execute(f'SELECT * FROM "{table}"{where}{ordering}', values)
            return [document for row in await cursor.fetchall() if (document := self._document(row)) is not None]
        finally:
            await connection.close()

    async def update(self, table: str, filters: dict[str, Any], updates: dict[str, Any]) -> bool:
        self._validate_table(table)
        if not updates:
            return False
        for field in updates:
            if field == "_id":
                raise ValueError("O identificador do registro não pode ser alterado.")
            self._validate_field(table, field)
        where, filter_values = self._where_clause(table, filters)
        assignments = ", ".join(f'"{field}" = ?' for field in updates)
        values = [self._serialize(value) for value in updates.values()]
        connection = await self._connect()
        try:
            cursor = await connection.execute(
                f'UPDATE "{table}" SET {assignments}{where}',
                [*values, *filter_values],
            )
            await connection.commit()
            return cursor.rowcount > 0
        finally:
            await connection.close()

    async def delete(self, table: str, filters: dict[str, Any]) -> bool:
        where, values = self._where_clause(table, filters)
        if not where:
            raise ValueError("A exclusão exige pelo menos um filtro.")
        connection = await self._connect()
        try:
            cursor = await connection.execute(f'DELETE FROM "{table}"{where}', values)
            await connection.commit()
            return cursor.rowcount > 0
        finally:
            await connection.close()

    async def delete_all(self, table: str) -> None:
        self._validate_table(table)
        connection = await self._connect()
        try:
            await connection.execute(f'DELETE FROM "{table}"')
            await connection.commit()
        finally:
            await connection.close()

    async def count(self, table: str, filters: dict[str, Any] | None = None) -> int:
        where, values = self._where_clause(table, filters or {})
        connection = await self._connect()
        try:
            cursor = await connection.execute(f'SELECT COUNT(*) FROM "{table}"{where}', values)
            row = await cursor.fetchone()
            return int(row[0])
        finally:
            await connection.close()

    async def sum(self, table: str, field: str, filters: dict[str, Any] | None = None) -> float:
        self._validate_field(table, field)
        where, values = self._where_clause(table, filters or {})
        connection = await self._connect()
        try:
            cursor = await connection.execute(
                f'SELECT COALESCE(SUM("{field}"), 0) FROM "{table}"{where}',
                values,
            )
            row = await cursor.fetchone()
            return float(row[0] or 0)
        finally:
            await connection.close()


database = SQLiteDatabase(_database_path())


async def ping_database() -> bool:
    try:
        await asyncio.wait_for(database.command("ping"), timeout=0.75)
        return True
    except (asyncio.TimeoutError, sqlite3.Error):
        return False
