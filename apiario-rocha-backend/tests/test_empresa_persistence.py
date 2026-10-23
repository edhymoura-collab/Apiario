import asyncio

from src.config.database import database
from src.services.empresa_service import obter_empresa, salvar_empresa
from src.services.empresa_service import obter_empresa_async, salvar_empresa_async


def test_salvar_e_obter_empresa():
    payload = {
        "razaoSocial": "Empresa Teste LTDA",
        "nomeFantasia": "Empresa Teste",
        "cnpj": "12.345.678/0001-99",
        "telefone": "(11) 99999-9999",
        "email": "contato@empresateste.com",
        "logoUrl": "https://example.com/logo.png",
    }

    saved = salvar_empresa(payload)
    assert saved["razaoSocial"] == "Empresa Teste LTDA"
    assert saved["nomeFantasia"] == "Empresa Teste"
    assert saved["logoUrl"] == "https://example.com/logo.png"

    loaded = obter_empresa()
    assert loaded["razaoSocial"] == "Empresa Teste LTDA"
    assert loaded["logoUrl"] == "https://example.com/logo.png"


def test_salvar_empresa_persiste_no_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "path", tmp_path / "empresa.db")

    async def save_and_reload():
        await salvar_empresa_async({"razaoSocial": "Apiário Rocha"})
        await salvar_empresa_async({"razaoSocial": "Apiário Rocha 4.0"})
        return await obter_empresa_async()

    loaded = asyncio.run(save_and_reload())

    assert loaded["razaoSocial"] == "Apiário Rocha 4.0"
