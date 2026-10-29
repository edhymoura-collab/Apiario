from src.auth.passwords import hash_password
from src.config.database import database


async def seed_sample_data() -> None:
    if await database.count("empresa") == 0:
        await database.insert("empresa", {
            "razaoSocial": "Apiário Rocha Ltda.",
            "nomeFantasia": "Apiário Rocha",
            "cnpj": "12.345.678/0001-90",
            "inscricaoEstadual": "123456789",
            "endereco": "Rua das Flores",
            "numero": "120",
            "complemento": "Sala 2",
            "bairro": "Centro",
            "cidade": "São João del Rei",
            "estado": "MG",
            "cep": "36300-000",
            "telefone": "(32) 3333-4444",
            "email": "contato@apiariorocha.com.br",
            "site": "https://apiariorocha.com.br",
            "segmento": "Apicultura",
            "logoUrl": "",
        })

    if await database.count("usuarios") == 0:
        await database.insert("usuarios", {
            "nome": "João da Silva",
            "email": "joao@apiariorocha.com.br",
            "username": "joao",
            "password": hash_password("Apiario@2026"),
            "perfil": "operador",
            "ativo": True,
            "data_cadastro": "2026-10-01T09:00:00",
        })
        await database.insert("usuarios", {
            "nome": "Maria Aparecida",
            "email": "maria@apiariorocha.com.br",
            "username": "maria",
            "password": hash_password("Apiario@2026"),
            "perfil": "gestor",
            "ativo": True,
            "data_cadastro": "2026-10-02T09:30:00",
        })

    if await database.count("administradores") == 0:
        await database.insert("administradores", {
            "nome": "Administrador Principal",
            "email": "admin@apiariorocha.com.br",
            "username": "admin",
            "password": hash_password("Admin@123456"),
            "nivel": "master",
            "ativo": True,
            "data_cadastro": "2026-10-01T08:00:00",
        })

    if await database.count("funcionarios") == 0:
        await database.insert("funcionarios", {
            "nome": "Carlos Mendes",
            "email": "carlos@apiariorocha.com.br",
            "cargo": "Apicultor",
            "departamento": "Campo",
            "salario": 4200.00,
            "status": "ativo",
            "observacoes": "Responsável pela rotina de colheita.",
            "ativo": True,
            "data_cadastro": "2026-10-01T07:00:00",
        })
        await database.insert("funcionarios", {
            "nome": "Ana Pereira",
            "email": "ana@apiariorocha.com.br",
            "cargo": "Analista de Qualidade",
            "departamento": "Laboratório",
            "salario": 4800.00,
            "status": "ativo",
            "observacoes": "Avalia pureza e qualidade do mel.",
            "ativo": True,
            "data_cadastro": "2026-10-05T09:00:00",
        })

    if await database.count("clientes") == 0:
        await database.insert("clientes", {
            "nome": "Mercado Verde",
            "email": "vendas@mercadoverde.com.br",
            "telefone": "(32) 98888-1234",
            "tipo": "comercial",
            "documento": "11.222.333/0001-44",
            "cidade": "Barbacena",
            "observacoes": "Cliente regular para venda em maior volume.",
            "ativo": True,
            "data_cadastro": "2026-10-02T14:00:00",
        })
        await database.insert("clientes", {
            "nome": "Casa do Campo",
            "email": "contato@casadocampo.com.br",
            "telefone": "(32) 97777-9911",
            "tipo": "varejo",
            "documento": "66.777.888/0001-99",
            "cidade": "Dona Eusébia",
            "observacoes": "Compra de produtos em pequenos lotes.",
            "ativo": True,
            "data_cadastro": "2026-10-06T16:00:00",
        })

    if await database.count("fornecedores") == 0:
        await database.insert("fornecedores", {
            "nome": "Fornecedora de Equipamentos Apícolas",
            "cnpj": "20.111.222/0001-77",
            "email": "contato@equipamentosapicolas.com.br",
            "telefone": "(31) 3333-5566",
            "categoria": "equipamentos",
            "cidade": "Belo Horizonte",
            "observacoes": "Fornecedor de caixas, telas e utensílios.",
            "ativo": True,
            "data_cadastro": "2026-10-03T11:00:00",
        })
        await database.insert("fornecedores", {
            "nome": "Mel e Natureza",
            "cnpj": "90.123.456/0001-10",
            "email": "vendas@melenatureza.com.br",
            "telefone": "(32) 5555-8899",
            "categoria": "matéria-prima",
            "cidade": "Lavras",
            "observacoes": "Fornecedor de embalagens e insumos.",
            "ativo": True,
            "data_cadastro": "2026-10-04T13:00:00",
        })

    if await database.count("colmeias") == 0:
        await database.insert("colmeias", {
            "codigo": "C-001",
            "nome": "Colmeia Norte 01",
            "localizacao": "Setor A",
            "status": "ativa",
            "observacoes": "Colmeia ativa e monitorada",
            "data_cadastro": "2026-10-01T06:00:00",
        })
        await database.insert("colmeias", {
            "codigo": "C-002",
            "nome": "Colmeia Sul 02",
            "localizacao": "Setor B",
            "status": "ativa",
            "observacoes": "Colmeia com melhor produção de primavera.",
            "data_cadastro": "2026-10-05T06:30:00",
        })

    if await database.count("lotes") == 0:
        await database.insert("lotes", {
            "codigo_lote": "LOT-001",
            "variedade_florada": "Eucalipto",
            "data_extracao": "2026-10-18",
            "umidade": 17.5,
            "pureza": 98.2,
            "quantidade_potes": 120,
            "laboratorio": "Laboratório de Qualidade",
            "storytelling": "Mel premium e rastreável",
            "auditado": True,
            "id_colmeia": "C-001",
            "criado_em": "2026-10-18T08:00:00",
        })

    if await database.count("produtos") == 0:
        await database.insert("produtos", {
            "nome": "Produto Exemplo 01 - Mel Artesanal",
            "codigo": "MEL-001",
            "categoria": "mel",
            "descricao": "Pote de mel artesanal do apiário",
            "preco": 35.5,
            "unidade": "pote",
            "ativo": True,
            "data_cadastro": "2026-10-01T10:00:00",
        })
        await database.insert("produtos", {
            "nome": "Produto Exemplo 02 - Pólen Natural",
            "codigo": "POL-002",
            "categoria": "produtos",
            "descricao": "Pólen apícola natural para consumo",
            "preco": 28.9,
            "unidade": "pacote",
            "ativo": True,
            "data_cadastro": "2026-10-01T10:30:00",
        })
        await database.insert("produtos", {
            "nome": "Produto Exemplo 03 - Própolis",
            "codigo": "PRO-003",
            "categoria": "suplemento",
            "descricao": "Cápsulas de própolis com selo de qualidade",
            "preco": 42.0,
            "unidade": "caixa",
            "ativo": True,
            "data_cadastro": "2026-10-01T11:00:00",
        })

    if await database.count("estoque") == 0:
        await database.insert("estoque", {
            "produto": "Produto Exemplo 01 - Mel Artesanal",
            "categoria": "mel",
            "quantidade": 48,
            "preco_unitario": 32.0,
            "estoque_minimo": 10,
            "unidade": "pote",
            "status": "normal",
            "criado_em": "2026-10-01T10:15:00",
            "atualizado_em": "2026-10-18T08:15:00",
        })
        await database.insert("estoque", {
            "produto": "Produto Exemplo 02 - Pólen Natural",
            "categoria": "produtos",
            "quantidade": 26,
            "preco_unitario": 25.0,
            "estoque_minimo": 8,
            "unidade": "pacote",
            "status": "normal",
            "criado_em": "2026-10-01T10:45:00",
            "atualizado_em": "2026-10-18T09:00:00",
        })

    if await database.count("vendas") == 0:
        await database.insert("vendas", {
            "codigo_venda": "VEN-001",
            "data_venda": "2026-10-18",
            "valor_bruto": 145.0,
            "valor_renda": 116.0,
            "valor_fundo": 29.0,
            "tipo_venda": "varejo",
            "forma_pagamento": "pix",
            "produto": "Produto Exemplo 01 - Mel Artesanal",
            "quantidade": 4,
            "status": "realizada",
            "criado_em": "2026-10-18T10:00:00",
        })
        await database.insert("vendas", {
            "codigo_venda": "VEN-002",
            "data_venda": "2026-10-20",
            "valor_bruto": 220.0,
            "valor_renda": 176.0,
            "valor_fundo": 44.0,
            "tipo_venda": "atacado",
            "forma_pagamento": "cartao",
            "produto": "Produto Exemplo 03 - Própolis",
            "quantidade": 5,
            "status": "realizada",
            "criado_em": "2026-10-20T11:30:00",
        })

    if await database.count("movimentacoes_financeiras") == 0:
        await database.insert("movimentacoes_financeiras", {
            "tipo": "entrada",
            "descricao": "Venda de mel artesanal",
            "categoria": "vendas",
            "valor": 145.0,
            "data_movimentacao": "2026-10-18",
            "forma_pagamento": "pix",
            "status": "realizada",
            "criado_em": "2026-10-18T10:05:00",
        })
        await database.insert("movimentacoes_financeiras", {
            "tipo": "saida",
            "descricao": "Compra de materiais de embalagem",
            "categoria": "insumos",
            "valor": 88.0,
            "data_movimentacao": "2026-10-19",
            "forma_pagamento": "transferencia",
            "status": "realizada",
            "criado_em": "2026-10-19T15:00:00",
        })

    if await database.count("telemetria") == 0:
        await database.insert("telemetria", {
            "id_colmeia": "C-001",
            "timestamp_utc": "2026-10-18T06:00:00Z",
            "peso_kg": 18.4,
            "temperatura_c": 26.8,
            "umidade_p": 61.0,
            "bateria_volt": 12.4,
            "criado_em": "2026-10-18T06:00:00Z",
        })
        await database.insert("telemetria", {
            "id_colmeia": "C-002",
            "timestamp_utc": "2026-10-18T07:00:00Z",
            "peso_kg": 20.1,
            "temperatura_c": 27.2,
            "umidade_p": 58.0,
            "bateria_volt": 12.8,
            "criado_em": "2026-10-18T07:00:00Z",
        })
