from fastapi.testclient import TestClient

from src.auth.security import get_current_user
from src.main import app

client = TestClient(app)


def test_cadastrar_usuario(monkeypatch):
    async def fake_criar_usuario(payload):
        return {"_id": "usuario_1", **payload}

    monkeypatch.setattr("src.routes.usuarios.criar_usuario", fake_criar_usuario)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/usuarios/cadastrar",
            json={
                "nome": "João Silva",
                "email": "joao@email.com",
                "username": "joao",
                "password": "123456",
                "perfil": "usuario",
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["username"] == "joao"


def test_cadastrar_administrador(monkeypatch):
    async def fake_criar_administrador(payload):
        return {"_id": "admin_1", **payload}

    monkeypatch.setattr("src.routes.administradores.criar_administrador", fake_criar_administrador)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/administradores/cadastrar",
            json={
                "nome": "Maria Admin",
                "email": "maria@email.com",
                "username": "maria",
                "password": "123456",
                "nivel": "master",
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["username"] == "maria"


def test_cadastrar_funcionario(monkeypatch):
    async def fake_criar_funcionario(payload):
        return {"_id": "func_1", **payload}

    monkeypatch.setattr("src.routes.funcionarios.criar_funcionario", fake_criar_funcionario)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/funcionarios/cadastrar",
            json={
                "nome": "Pedro Funcionário",
                "email": "pedro@email.com",
                "cargo": "Operador",
                "departamento": "Produção",
                "salario": 3500.0,
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["cargo"] == "Operador"


def test_cadastrar_venda(monkeypatch):
    async def fake_registrar_venda(payload):
        return {
            "_id": "venda_1",
            "codigo_venda": payload["codigo_venda"],
            "valor_bruto": payload["valor_bruto"],
            "valor_renda": payload["valor_bruto"] * 0.7,
            "valor_fundo": payload["valor_bruto"] * 0.3,
            "tipo_venda": payload["tipo_venda"],
        }

    monkeypatch.setattr("src.routes.financeiro.registrar_venda", fake_registrar_venda)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/vendas/registrar",
            json={
                "codigo_venda": "VEN-001",
                "data_venda": "2026-10-21",
                "valor_bruto": 1000.0,
                "tipo_venda": "venda direta",
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["codigo_venda"] == "VEN-001"


def test_listar_e_manipular_usuarios(monkeypatch):
    async def fake_listar_usuarios():
        return [{"_id": "u1", "nome": "Alice", "email": "alice@email.com", "username": "alice", "perfil": "usuario"}]

    async def fake_atualizar_usuario(_id, payload):
        return {"_id": _id, **payload}

    async def fake_excluir_usuario(_id):
        return {"_id": _id, "removido": True}

    monkeypatch.setattr("src.routes.usuarios.listar_usuarios", fake_listar_usuarios)
    monkeypatch.setattr("src.routes.usuarios.atualizar_usuario", fake_atualizar_usuario)
    monkeypatch.setattr("src.routes.usuarios.excluir_usuario", fake_excluir_usuario)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        list_response = client.get("/api/v1/usuarios")
        update_response = client.put("/api/v1/usuarios/u1", json={"nome": "Alice Nova", "email": "alice@email.com", "username": "alice", "password": "123456", "perfil": "usuario"})
        delete_response = client.delete("/api/v1/usuarios/u1")
    finally:
        app.dependency_overrides.clear()

    assert list_response.status_code == 200
    assert update_response.status_code == 200
    assert delete_response.status_code == 200
