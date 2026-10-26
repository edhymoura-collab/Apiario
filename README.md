# Apiário Rocha 4.0

Aplicação web para apoiar a gestão de um apiário. O sistema reúne cadastros, catálogo de produtos, estoque, vendas e informações de produção, com uma API REST e consulta pública de rastreabilidade de lotes auditados.

## Funcionalidades

- Painel administrativo web servido pelo próprio backend.
- Gestão de usuários, administradores, funcionários, clientes, fornecedores e dados da empresa.
- Catálogo de produtos separado do controle de inventário.
- Controle de estoque, alertas e relatórios.
- Registro de vendas e divisão financeira de 70% para renda e 30% para o fundo de modernização.
- API para colmeias, leituras de telemetria e lotes de produção.
- Consulta pública de rastreabilidade para lotes auditados.
- Autenticação administrativa com JWT e armazenamento local em SQLite.

O painel ainda não oferece formulários completos para todas as operações de colmeias, lotes, telemetria, rastreabilidade e finanças. Consulte o README do backend para conhecer os limites atuais e a lista de endpoints.

## Tecnologias

- **Interface:** HTML, CSS e JavaScript.
- **Backend/API:** Python 3.11+, FastAPI e Pydantic.
- **Persistência:** SQLite com acesso assíncrono via aiosqlite.
- **Testes:** pytest.
- **Documentação interativa da API:** Swagger/OpenAPI, disponível em `/docs`.

## Estrutura do repositório

```text
.
├── 01-visao-geral.md
├── 02-requisitos.md
├── 03-arquitetura.md
├── 04-modelagem-dados-e-api.md
├── roteiro-apresentacao.md
├── apiario-rocha-backend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   ├── requirements.txt
│   ├── src/
│   └── tests/
└── data/
    └── apiario.db
```

O banco SQLite padrão fica em `data/apiario.db`. O arquivo e as tabelas são criados automaticamente quando necessário; é possível alterar o caminho com `SQLITE_PATH`.

## Executar localmente

É necessário ter Python 3.11 ou superior. A instalação, configuração do `.env` e instruções para Windows, Linux e macOS estão detalhadas no [README do backend](./apiario-rocha-backend/README.md).

Resumo para Windows PowerShell, executado a partir da raiz do repositório:

```powershell
Set-Location .\apiario-rocha-backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edite `apiario-rocha-backend/.env` e configure pelo menos `SECRET_KEY`, `ADMIN_USERNAME` e `ADMIN_PASSWORD`, conforme os requisitos descritos no [README do backend](./apiario-rocha-backend/README.md). Em seguida, inicie a aplicação:

```powershell
python -m uvicorn src.main:app --reload
```

Endereços locais padrão:

- Painel: <http://127.0.0.1:8000/>
- Documentação interativa da API: <http://127.0.0.1:8000/docs>
- Verificação de saúde: <http://127.0.0.1:8000/health>

## Executar os testes

Na pasta `apiario-rocha-backend`, com o ambiente virtual ativado:

```powershell
$env:PYTHONPATH = "."
python -m pytest tests -q
```

## Segurança

Não versione nem compartilhe o arquivo `.env` ou credenciais reais. Use uma chave JWT aleatória com pelo menos 32 caracteres e uma senha administrativa exclusiva com pelo menos 12 caracteres.

Na implementação atual, as rotas de telemetria são públicas. Antes de disponibilizar a aplicação em uma rede pública, restrinja o acesso a essas rotas e revise a implantação; CORS não substitui autenticação. Consulte a seção de segurança do [README do backend](./apiario-rocha-backend/README.md) para mais detalhes.

## Documentação

- [Visão geral da solução](./01-visao-geral.md)
- [Requisitos do sistema](./02-requisitos.md)
- [Arquitetura técnica](./03-arquitetura.md)
- [Modelagem de dados e contratos da API](./04-modelagem-dados-e-api.md)
- [Instalação, configuração e operação do backend](./apiario-rocha-backend/README.md)
- [Roteiro de apresentação](./roteiro-apresentacao.md)
