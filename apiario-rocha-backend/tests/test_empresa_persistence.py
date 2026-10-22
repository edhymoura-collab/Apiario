from src.services.empresa_service import obter_empresa, salvar_empresa


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
