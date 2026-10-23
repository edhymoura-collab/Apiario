# Fase 3 — Arquitetura Técnica da Solução

## 1. Objetivo

Este documento descreve a arquitetura implementada no Apiário Rocha 4.0: painel web estático servido pelo FastAPI, endpoints organizados por domínio, regras de serviço, validação Pydantic e persistência SQLite assíncrona.

## 2. Visão de contexto

```text
Navegador
  ├── HTML/CSS/JavaScript (painel administrativo)
  ├── POST /api/v1/auth/login
  └── chamadas REST com Authorization: Bearer <JWT>
             │
             ▼
          FastAPI
  ├── middleware CORS
  ├── rotas e autenticação
  ├── modelos Pydantic
  ├── serviços de domínio
  └── acesso SQLite (aiosqlite)
             │
             ▼
       data/apiario.db
```

O mesmo processo FastAPI entrega a interface e a API. Dessa forma, o painel usa a origem atual do navegador para construir a URL da API, evitando configuração de host distinta na instalação padrão.

## 3. Componentes e responsabilidades

### 3.1 Apresentação

- `index.html`: módulos, formulários, tabelas e diálogo de autenticação.
- `styles.css`: tema, layout responsivo e estados dos componentes.
- `script.js`: troca de telas, validação nativa de formulários, chamadas REST, autenticação, tabelas, pesquisa, paginação e exportação CSV.
- As rotas `/`, `/static/styles.css` e `/static/script.js` servem os arquivos da interface.

O painel abre o diálogo de autenticação quando uma operação precisa de um token. O token JWT fica em `localStorage` até a ação de saída ou sua expiração. As chamadas protegidas recebem o cabeçalho `Authorization: Bearer <token>`.

### 3.2 API

`src/main.py` configura o ciclo de vida da aplicação, CORS, resposta de saúde, arquivos estáticos e inclusão dos roteadores. Os roteadores ficam em `src/routes/` e definem o contrato HTTP e os limites de autenticação.

O FastAPI gera o OpenAPI em `/openapi.json` e a interface Swagger em `/docs`. A documentação OpenAPI indica quais rotas usam Bearer JWT.

### 3.3 Validação e domínio

- `src/models/`: contratos Pydantic e validações de entrada.
- `src/services/`: cadastro, atualização, remoção, telemetria, rastreabilidade, estoque e regras financeiras.
- `src/auth/`: emissão e validação de JWT e hashing/verificação de senhas.
- `src/config/settings.py`: configuração por variáveis de ambiente.

Os serviços de cadastro são compartilhados pelas rotas de usuários, administradores, funcionários, clientes e fornecedores. Produtos e estoque mantêm modelos, serviços e tabelas separados.

### 3.4 Persistência

`src/config/database.py` implementa o acesso SQLite com aiosqlite. A lista permitida de tabelas e campos evita aceitar identificadores SQL arbitrários. O acesso serializa datas em ISO 8601 e booleanos como inteiros.

Na inicialização:

1. cria tabelas e índices que ainda não existem;
2. migra senhas antigas em texto puro para hashes scrypt;
3. carrega dados de amostra de colmeias e lotes somente quando as tabelas correspondentes estão vazias.

O caminho padrão do banco é `../data/apiario.db`, relativo ao diretório `apiario-rocha-backend`; `SQLITE_PATH` pode alterá-lo.

## 4. Estrutura de diretórios implementada

```text
apiario-rocha-backend/
├── index.html
├── script.js
├── styles.css
├── requirements.txt
├── .env.example
└── src/
    ├── main.py
    ├── auth/
    │   ├── passwords.py
    │   └── security.py
    ├── config/
    │   ├── database.py
    │   └── settings.py
    ├── models/
    ├── routes/
    └── services/
```

Os módulos são nomeados por domínio; consulte o código e `/docs` para a lista exata de rotas e schemas vigentes.

## 5. Segurança e limites

### 5.1 Login administrativo

- `ADMIN_USERNAME` e `ADMIN_PASSWORD` são lidos da configuração local do servidor.
- A aplicação não contém uma credencial administrativa fixa de fallback.
- Senhas administrativas devem ter pelo menos 12 caracteres.
- A ausência dessas configurações faz o login retornar `503`, em vez de aceitar uma identidade padrão.

### 5.2 JWT

- `SECRET_KEY` deve conter pelo menos 32 caracteres; não há chave de assinatura padrão.
- O algoritmo padrão é HS256; a duração do token é configurável por `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Rotas protegidas respondem `401` sem Bearer token válido.
- A aplicação não implementa papéis, escopos, renovação, revogação de token ou sessão HTTP-only; a autenticação é baseada em token bearer mantido no navegador.

### 5.3 Senhas de cadastros

- Senhas de usuários e administradores cadastrados são derivadas com scrypt, salt aleatório e comparação em tempo constante.
- As respostas de listagem e atualização removem o campo `password`.
- A inicialização migra registros legados em texto puro. É necessário manter uma cópia de segurança do SQLite antes de uma atualização operacional relevante.
- As contas cadastradas no módulo de usuários não são usadas atualmente como credenciais de login do painel; o login utiliza apenas as variáveis `ADMIN_*`.

### 5.4 Rotas públicas

- `GET /api/v1/rastreabilidade/{codigo_lote}` é público e retorna somente dados públicos do lote auditado.
- `POST /api/v1/telemetria` e `GET /api/v1/telemetria/{id_colmeia}` também são públicos na implementação atual. Integrações de sensor devem ser isoladas e protegidas por uma camada confiável; autenticação própria, rate limiting e limites contra abuso ainda não fazem parte desta implementação.
- CORS controla origens de navegador, não substitui autenticação nem é uma barreira contra chamadas diretas à API.

## 6. Fluxos principais

### 6.1 Acesso ao painel

1. O navegador solicita o HTML e os assets.
2. Uma chamada protegida tenta usar o JWT existente.
3. Sem token, o painel solicita usuário e senha administrativos.
4. A API valida as credenciais configuradas e emite JWT com expiração.
5. O navegador mantém o token até sair ou receber uma resposta de token inválido; solicitações podem pedir novo login e repetir uma única chamada.

### 6.2 Cadastro de produto

1. A interface envia JSON a `POST /api/v1/produtos/cadastrar`.
2. FastAPI valida o conteúdo por `ProdutoCreate`.
3. O serviço grava o registro na tabela `produtos`.
4. A interface atualiza as coleções e renderiza o catálogo.

O catálogo não insere ou altera registros na tabela `estoque`.

### 6.3 Venda

1. O endpoint protegido valida o payload de venda.
2. O serviço calcula renda e fundo a partir do valor bruto e persiste a transação.
3. Quando há produto e quantidade, a regra de baixa automática interage com o estoque correspondente.
4. Resumos financeiros consultam os dados persistidos.

## 7. Configuração operacional

Variáveis principais:

| Variável | Obrigatória para login/API protegida | Finalidade |
|---|---:|---|
| `SECRET_KEY` | Sim | Assinatura e validação JWT; mínimo de 32 caracteres. |
| `ADMIN_USERNAME` | Sim para login | Nome de usuário administrativo. |
| `ADMIN_PASSWORD` | Sim para login | Senha administrativa; mínimo de 12 caracteres. |
| `ALGORITHM` | Não | Algoritmo JWT; padrão HS256. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Validade do JWT em minutos; padrão 60. |
| `SQLITE_PATH` | Não | Caminho do arquivo SQLite; padrão `../data/apiario.db`. |
| `CORS_ORIGINS` | Não | Lista de origens habilitadas para navegador, conforme suporte de configuração. |

Armazenar `.env` localmente, fora do controle de versão, e não compartilhar seus valores. Os passos de instalação e geração de uma chave segura estão no [README operacional](./apiario-rocha-backend/README.md).

## 8. Observabilidade e tratamento de erros

- Uvicorn registra ciclo de vida e requisições no terminal.
- Erros de validação Pydantic retornam `422`; autenticação retorna `401`; registros de rastreabilidade ausentes ou não auditados retornam `404`.
- Exceções de banco nos roteadores de domínio são expostas como erros JSON com mensagens de operação; o handler global evita devolver stack trace.
- A implementação atual não configura logging estruturado, métricas, tracing, rate limiting ou exportação para um provedor externo.

## 9. Testes

Os testes de backend ficam em `apiario-rocha-backend/tests/` e cobrem rotas, persistência SQLite, cadastro, cálculos de estoque/finanças e segurança. Execute a suíte a partir da pasta do backend:

```powershell
$env:PYTHONPATH = "."
..\.venv\Scripts\python.exe -m pytest tests -q
```

Adapte o caminho do interpretador caso esteja usando outro ambiente virtual.
