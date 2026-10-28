from fastapi.testclient import TestClient
from jose import jwt

from src.auth.security import create_access_token, get_current_user
from src.config.settings import get_settings
from src.main import app


settings = get_settings()
client = TestClient(app)


def test_create_access_token_encodes_subject():
    token = create_access_token("admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

    assert payload["sub"] == "admin"


def test_login_route_returns_access_token(monkeypatch):
    from src.routes.auth import authenticate_user

    async def fake_authenticate_user(username: str, password: str):
        return {"username": username, "password": password}

    monkeypatch.setattr("src.routes.auth.authenticate_user", fake_authenticate_user)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_colmeia_route_requires_auth(monkeypatch):
    def fake_get_current_user():
        return "admin"

    async def fake_criar_colmeia(payload):
        return {"_id": "colmeia_1", **payload}

    monkeypatch.setattr("src.routes.colmeias.criar_colmeia", fake_criar_colmeia)
    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.post(
            "/api/v1/colmeias",
            json={
                "codigo": "C-001",
                "nome": "Colmeia Norte 01",
                "localizacao": "Setor A",
                "status": "ativa",
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["codigo"] == "C-001"


def test_listar_colmeias_retorna_lista(monkeypatch):
    async def fake_listar_colmeias():
        return [{"_id": "colmeia_1", "codigo": "C-001", "nome": "Colmeia Norte 01"}]

    monkeypatch.setattr("src.routes.colmeias.listar_colmeias", fake_listar_colmeias)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.get("/api/v1/colmeias")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["colmeias"][0]["codigo"] == "C-001"


def test_rastreabilidade_publica_retorna_lote(monkeypatch):
    async def fake_buscar_lote_publico(codigo_lote: str):
        return {
            "codigo_lote": codigo_lote,
            "variedade_florada": "Eucalipto",
            "data_extracao": "2026-10-18",
            "umidade": 17.5,
            "pureza": 98.2,
            "quantidade_potes": 120,
            "laboratorio": "Laboratório de Qualidade",
            "storytelling": "Mel premium",
        }

    monkeypatch.setattr("src.routes.rastreabilidade.buscar_lote_publico", fake_buscar_lote_publico)

    response = client.get("/api/v1/rastreabilidade/LOT-001")

    assert response.status_code == 200
    assert response.json()["codigo_lote"] == "LOT-001"


def test_criar_lote_requer_autenticacao(monkeypatch):
    async def fake_criar_lote(payload):
        return {"_id": "lote_1", **payload}

    monkeypatch.setattr("src.routes.lotes.criar_lote", fake_criar_lote)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.post(
            "/api/v1/lotes",
            json={
                "codigo_lote": "LOT-002",
                "variedade_florada": "Eucalipto",
                "data_extracao": "2026-10-19",
                "umidade": 18.0,
                "pureza": 97.5,
                "quantidade_potes": 90,
                "laboratorio": "Laboratório de Qualidade",
                "storytelling": "Mel de alta qualidade",
                "auditado": True,
            },
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["codigo_lote"] == "LOT-002"


def test_dashboard_resumo_fallback_quando_banco_falha(monkeypatch):
    async def fake_obter_resumo_operacional():
        raise RuntimeError("MongoDB indisponível")

    monkeypatch.setattr("src.routes.financeiro.obter_resumo_operacional", fake_obter_resumo_operacional)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.get("/api/v1/dashboard/resumo")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "admin"
    assert data["total_vendas"] == 142
    assert data["fundo_acumulado"] == 48700


def test_financeiro_root_alias_returns_summary(monkeypatch):
    async def fake_obter_resumo_operacional():
        return {
            "total_vendas": 42,
            "total_funcionarios": 10,
            "fundo_acumulado": 3500,
            "faturamento_mes": 2800,
            "total_clientes": 8,
            "total_fornecedores": 5,
            "estoque_total": 120,
        }

    monkeypatch.setattr("src.routes.financeiro.obter_resumo_operacional", fake_obter_resumo_operacional)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.get("/api/v1/financeiro")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "admin"
    assert data["total_vendas"] == 42
    assert data["fundo_acumulado"] == 3500


def test_listar_vendas_fallback_quando_banco_falha(monkeypatch):
    async def fake_listar_vendas():
        raise RuntimeError("MongoDB indisponível")

    monkeypatch.setattr("src.routes.financeiro.listar_vendas", fake_listar_vendas)
    app.dependency_overrides[get_current_user] = lambda: "admin"

    try:
        response = client.get("/api/v1/vendas")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "admin"
    assert data["vendas"][0]["codigo_venda"] == "VND-101"
