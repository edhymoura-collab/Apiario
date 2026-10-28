import asyncio

from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from src.auth.passwords import hash_password, is_password_hash, verify_password
from src.auth.security import create_access_token, get_current_user
from src.config.database import SQLiteDatabase, database
from src.config.settings import get_settings
from src.main import app
from src.services.cadastros_service import (
    atualizar_usuario,
    criar_usuario,
    listar_usuarios,
)


client = TestClient(app)


def test_scrypt_password_hash_verifies_without_storing_plaintext():
    password = "senha-forte-de-teste"
    stored_value = hash_password(password)

    assert is_password_hash(stored_value)
    assert stored_value != password
    assert verify_password(password, stored_value)
    assert not verify_password("senha-incorreta", stored_value)


def test_login_uses_configured_credentials_and_rejects_old_defaults(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "admin_username", "secure-admin")
    monkeypatch.setattr(settings, "admin_password", "senha-configurada-segura")

    valid_response = client.post(
        "/api/v1/auth/login",
        json={"username": "secure-admin", "password": "senha-configurada-segura"},
    )
    old_default_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert valid_response.status_code == 200
    assert "access_token" in valid_response.json()
    assert old_default_response.status_code == 401


def test_login_accepts_short_configured_admin_password(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "admin_username", "admin")
    monkeypatch.setattr(settings, "admin_password", "admin")

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["perfil"] == "admin"


def test_get_current_user_decodes_valid_bearer_token():
    token = create_access_token("admin", perfil="admin")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    assert get_current_user(credentials) == "admin"


def test_user_password_is_hashed_and_never_returned_by_api(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "apiario.db")
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        with TestClient(app) as test_client:
            create_response = test_client.post(
                "/api/v1/usuarios/cadastrar",
                json={
                    "nome": "Usuária de teste",
                    "email": "usuario@example.invalid",
                    "username": "usuario_teste",
                    "password": "senha-original-123",
                },
            )
            list_response = test_client.get("/api/v1/usuarios")
            update_response = test_client.put(
                f"/api/v1/usuarios/{create_response.json()['id_usuario']}",
                json={"password": "nova-senha-original-456"},
            )
            stored_user = asyncio.run(
                database.find_one("usuarios", {"username": "usuario_teste"})
            )
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert "password" not in create_response.json()
    assert list_response.status_code == 200
    assert "password" not in list_response.json()["usuarios"][0]
    assert update_response.status_code == 200
    assert "password" not in update_response.json()["usuario_atualizado"]
    assert stored_user is not None
    assert verify_password("nova-senha-original-456", stored_user["password"])


def test_database_startup_migrates_legacy_plaintext_passwords(tmp_path):
    test_database = SQLiteDatabase(tmp_path / "legacy.db")

    async def seed_and_migrate():
        await test_database.insert(
            "usuarios",
            {"username": "legacy-user", "password": "legacy-password"},
        )
        await test_database.insert(
            "administradores",
            {"username": "legacy-admin", "password": "legacy-admin-password"},
        )
        await test_database.initialize()
        return (
            await test_database.find_one("usuarios", {"username": "legacy-user"}),
            await test_database.find_one("administradores", {"username": "legacy-admin"}),
        )

    user, administrator = asyncio.run(seed_and_migrate())

    assert user is not None
    assert administrator is not None
    assert is_password_hash(user["password"])
    assert is_password_hash(administrator["password"])
    assert verify_password("legacy-password", user["password"])
    assert verify_password("legacy-admin-password", administrator["password"])
