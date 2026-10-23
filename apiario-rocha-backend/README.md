# Apiário Rocha 4.0

Aplicação web e API REST para cadastros e gestão do apiário, catálogo de produtos, inventário, vendas, finanças, colmeias, telemetria e rastreabilidade de lotes.

## 1. Visão geral

- **Interface:** HTML, CSS e JavaScript, servidos pela mesma aplicação FastAPI.
- **API:** FastAPI com validação Pydantic e documentação OpenAPI.
- **Banco:** arquivo SQLite local acessado com aiosqlite.
- **Autenticação:** JWT Bearer para as operações internas.
- **Documentação e execução detalhada:** os documentos na raiz do repositório descrevem [visão geral](../01-visao-geral.md), [requisitos](../02-requisitos.md), [arquitetura](../03-arquitetura.md) e [modelagem e contratos](../04-modelagem-dados-e-api.md).

## 2. Requisitos

- Python 3.11 ou superior.
- Windows PowerShell, Linux ou macOS.
- SQLite, incluído no Python; não é necessário instalar um servidor de banco.

## 3. Instalação no Windows

Execute os comandos a partir da pasta `apiario-rocha-backend`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se a política do PowerShell impedir a ativação, use o interpretador do ambiente diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Instalação no Linux ou macOS

Execute os comandos a partir desta pasta:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configuração local obrigatória

Copie `.env.example` para `.env` sem sobrescrever uma configuração existente:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

```bash
test -f .env || cp .env.example .env
```

Edite `.env` localmente e substitua os marcadores:

| Variável | Obrigatória | Finalidade e validação |
|---|---:|---|
| `SECRET_KEY` | Sim para autenticação e rotas protegidas | Chave JWT aleatória com pelo menos 32 caracteres. A aplicação não possui segredo padrão. |
| `ADMIN_USERNAME` | Sim para login | Usuário administrativo da instalação. |
| `ADMIN_PASSWORD` | Sim para login | Senha administrativa exclusiva com pelo menos 12 caracteres. |
| `ALGORITHM` | Não | Algoritmo de assinatura JWT; o padrão é `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Validade do JWT em minutos; o padrão é `60`. |
| `SQLITE_PATH` | Não | Arquivo do banco, relativo à pasta do backend quando não for absoluto; padrão `../data/apiario.db`. |
| `APP_NAME` | Não | Nome da API e documentação. |
| `COMPANY_NAME` | Não | Nome da empresa exibido na descrição da API. |
| `CORS_ORIGINS` | Não | Origens de navegador permitidas, de acordo com o formato de lista do `pydantic-settings`. |

Gere valores aleatórios em vez de usar exemplos copiados:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Execute o comando duas vezes para obter uma chave JWT e uma senha administrativa diferentes. Copie os valores diretamente para `.env` e mantenha o arquivo fora do controle de versão. O `.gitignore` do repositório já ignora `.env`.

**Nunca** publique valores de `.env`, inclua-os em capturas de tela, tickets ou commits. Se um segredo for exposto, substitua-o e reinicie a API. Alterar `SECRET_KEY` invalida todos os tokens anteriormente emitidos.

## 6. Inicialização e primeiro acesso

Com o ambiente virtual ativado, inicie o servidor a partir desta pasta:

```powershell
python -m uvicorn src.main:app --reload
```

No Linux/macOS, o mesmo comando pode ser usado após ativar o ambiente.

Se o ambiente `apiario-rocha-backend-py311` já existir na raiz do repositório, no Windows também é possível iniciar sem ativação:

```powershell
..\apiario-rocha-backend-py311\Scripts\python.exe -m uvicorn src.main:app --reload
```

Endereços locais padrão:

- Painel: <http://127.0.0.1:8000/>
- Swagger/OpenAPI: <http://127.0.0.1:8000/docs>
- Especificação OpenAPI: <http://127.0.0.1:8000/openapi.json>
- Saúde do processo: <http://127.0.0.1:8000/health>

O diálogo de login aparece quando o painel precisa de uma rota protegida. Use `ADMIN_USERNAME` e `ADMIN_PASSWORD` definidos no `.env`. A API responde `503` quando as credenciais ou uma chave JWT segura não estão configuradas; ela não permite continuar com credenciais padrão.

O endpoint de saúde é público e verifica apenas que a aplicação está respondendo; não substitui um monitoramento da conectividade e integridade do banco.

## 7. Autenticação e segurança

### 7.1 Fluxo de autenticação

1. O painel envia `username` e `password` para `POST /api/v1/auth/login`.
2. A API compara as credenciais administrativas configuradas no servidor.
3. Em caso de sucesso, retorna um JWT Bearer com expiração.
4. O painel armazena o token em `localStorage` e envia `Authorization: Bearer <token>` às rotas protegidas.
5. Ao sair, o token local é removido. Um token expirado exige nova autenticação.

O armazenamento em `localStorage` permite que scripts executados na mesma origem acessem o token; publique o sistema somente em ambiente confiável e use HTTPS quando houver acesso por rede.

### 7.2 Credenciais de usuários cadastrados

Senhas de usuários e administradores criados pelos módulos de cadastro são derivadas por scrypt com salt aleatório. O campo `password` é omitido das respostas de listagem e atualização. Senhas legadas em texto puro são migradas para hash durante a inicialização do banco.

Os registros cadastrados em `/api/v1/usuarios` e `/api/v1/administradores` **não** autenticam o painel nesta versão. O acesso administrativo usa as duas variáveis `ADMIN_*`; o sistema ainda não sincroniza contas com permissões, não oferece papéis granulares nem recuperação de senha.

### 7.3 Endpoints públicos e limitações

- `GET /api/v1/rastreabilidade/{codigo_lote}` é público e retorna dados apenas de lotes auditados.
- `POST /api/v1/telemetria` e `GET /api/v1/telemetria/{id_colmeia}` são públicos na implementação atual. Restrinja-os à rede confiável até que seja implementada autenticação apropriada para dispositivos.
- CORS limita origens de navegadores e não bloqueia chamadas HTTP diretas.
- Não há rate limiting, revogação de token, papéis/permissões granulares, auditoria de segurança estruturada ou proteção anti-abuso nas rotas públicas.

## 8. Endpoints disponíveis

Todas as rotas abaixo usam o prefixo `/api/v1`, exceto `/health`. Para a especificação de payloads e schemas, consulte `/docs` ou [modelagem e contratos](../04-modelagem-dados-e-api.md).

| Domínio | Operações | Acesso |
|---|---|---|
| Autenticação | `POST /auth/login` | Público |
| Usuários | `GET /usuarios`, `POST /usuarios/cadastrar`, `PUT /usuarios/{usuario_id}`, `DELETE /usuarios/{usuario_id}` | Bearer JWT |
| Administradores | `GET /administradores`, `POST /administradores/cadastrar`, `PUT /administradores/{administrador_id}`, `DELETE /administradores/{administrador_id}` | Bearer JWT |
| Funcionários | `GET /funcionarios`, `POST /funcionarios/cadastrar`, `PUT /funcionarios/{funcionario_id}`, `DELETE /funcionarios/{funcionario_id}` | Bearer JWT |
| Clientes | `GET /clientes`, `POST /clientes/cadastrar`, `PUT /clientes/{cliente_id}`, `DELETE /clientes/{cliente_id}` | Bearer JWT |
| Fornecedores | `GET /fornecedores`, `POST /fornecedores/cadastrar`, `PUT /fornecedores/{fornecedor_id}`, `DELETE /fornecedores/{fornecedor_id}` | Bearer JWT |
| Empresa | `GET /empresa`, `PUT /empresa` | Bearer JWT |
| Colmeias | `GET /colmeias`, `POST /colmeias` | Bearer JWT |
| Telemetria | `POST /telemetria`, `GET /telemetria/{id_colmeia}` | Público atualmente |
| Lotes | `GET /lotes`, `POST /lotes`, `GET /lotes/{codigo_lote}` | Bearer JWT |
| Rastreabilidade | `GET /rastreabilidade/{codigo_lote}` | Público |
| Produtos | `GET /produtos`, `POST /produtos/cadastrar`, `PUT /produtos/{produto_id}`, `DELETE /produtos/{produto_id}` | Bearer JWT |
| Estoque | `GET /estoque`, `POST /estoque/cadastrar`, `PUT /estoque/{item_id}`, `DELETE /estoque/{item_id}`, `GET /estoque/alertas`, `GET /estoque/relatorio` | Bearer JWT |
| Vendas | `GET /vendas`, `POST /vendas/registrar`, `PUT /vendas/{venda_id}`, `DELETE /vendas/{venda_id}` | Bearer JWT |
| Financeiro | `GET /financeiro/fundo-acumulado` | Bearer JWT |
| Indicadores | `GET /dashboard/resumo`, `GET /relatorios/resumo` | Bearer JWT |
| Saúde | `GET /health` | Público |

## 9. Catálogo de produtos e estoque

O módulo **Produtos** guarda dados comerciais: nome, código opcional, categoria, descrição, preço, unidade e status ativo. O módulo **Estoque** guarda a quantidade física, o preço unitário, o mínimo e os alertas.

Os dois módulos têm tabelas distintas. Criar, editar ou remover um produto no catálogo não cria, ajusta nem exclui automaticamente um item de estoque. As vendas podem registrar o nome do produto como texto e, com quantidade, aplicar as regras de baixa automática de estoque implementadas no serviço de vendas.

## 10. Banco de dados, inicialização e backup

Por padrão, o SQLite é armazenado em `../data/apiario.db`, uma pasta acima da raiz pública do backend. O banco e o diretório são criados automaticamente. Personalize o caminho com `SQLITE_PATH`.

Na inicialização, a aplicação:

1. cria as tabelas e índices inexistentes;
2. migra as senhas legadas em texto puro de usuários e administradores para scrypt;
3. carrega registros de amostra para colmeias e lotes somente se cada uma dessas tabelas estiver vazia.

As migrations automáticas de senha alteram o arquivo SQLite. Faça uma cópia de segurança antes de atualização, migração ou operação de manutenção. Para backup consistente com o servidor ativo, use as ferramentas de backup do SQLite ou pare o processo antes de copiar o arquivo.

## 11. Interface administrativa

O painel implementa tabelas, formulários CRUD, pesquisa, paginação e exportação CSV para usuários, administradores, funcionários, clientes, fornecedores, vendas, estoque e produtos. Empresa usa formulário próprio.

Colmeias, lotes, telemetria, rastreabilidade e finanças também possuem endpoints de API, mas partes dessas áreas ainda são telas informativas ou indicadores, não formulários administrativos completos. Verifique a seção correspondente no painel antes de presumir que toda operação da API já possui fluxo visual.

## 12. Executar os testes

Execute na pasta do backend com o ambiente virtual ativado:

```powershell
$env:PYTHONPATH = "."
python -m pytest tests -q
```

Com o ambiente `apiario-rocha-backend-py311` na raiz do repositório:

```powershell
$env:PYTHONPATH = "."
..\apiario-rocha-backend-py311\Scripts\python.exe -m pytest tests -q
```

Os testes em `tests/` cobrem rotas, autenticação, hashing e migração de senhas, persistência, estoques, produtos e regras financeiras. A suíte usa configurações exclusivas para testes por meio de `tests/conftest.py`; não use esses valores em uma implantação real.

## 13. Erros esperados

| HTTP | Significado comum |
|---:|---|
| `200` | Consulta ou operação concluída. |
| `201` | Registro criado. |
| `401` | Token ausente, inválido ou credenciais de login incorretas. |
| `404` | Lote não localizado ou indisponível para consulta pública. |
| `422` | JSON ausente ou campos fora das regras do modelo Pydantic. |
| `500` | Erro interno da operação ou da persistência; a resposta não deve revelar stack trace. |
| `503` | Configuração administrativa ou chave JWT ausente/insegura. |

## 14. Solução de problemas

### O painel abre, mas solicita login repetidamente

Confirme que o `.env` foi criado dentro de `apiario-rocha-backend`, que `SECRET_KEY` tem pelo menos 32 caracteres e que usuário e senha correspondem a `ADMIN_USERNAME` e `ADMIN_PASSWORD`. Reinicie o processo após alterar `.env`.

### A API responde `503` em rotas autenticadas

Configure o segredo JWT e as credenciais administrativas seguindo a seção 5. Não remova as validações para contornar o erro.

### A API responde `401` após trocar a chave JWT

Esse comportamento é esperado. A chave nova invalida tokens antigos; saia do painel ou recarregue a página e autentique-se novamente.

### Um cadastro retorna `422`

Consulte `detail` na resposta ou `/docs` para identificar os campos inválidos e respeitar os limites do modelo.

### O SQLite parece vazio

Verifique o caminho resolvido pelo `SQLITE_PATH` e a mensagem `SQLite conectado` no terminal. Caminhos relativos são resolvidos a partir do backend.

## 15. Documentação de produto

- [Roteiro de apresentação do sistema](../roteiro-apresentacao.md)
- [Visão geral](../01-visao-geral.md)
- [Requisitos](../02-requisitos.md)
- [Arquitetura](../03-arquitetura.md)
- [Modelagem de dados e contratos de API](../04-modelagem-dados-e-api.md)
