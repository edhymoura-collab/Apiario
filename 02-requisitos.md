# Fase 2 — Requisitos do Sistema Apiário Rocha 4.0

## 1. Objetivo e estado

Este documento consolida os requisitos funcionais e não funcionais do sistema. Requisitos descritos como disponíveis refletem a API e a interface atuais; limitações e comportamentos ainda não implementados são indicados explicitamente para não confundir planejamento com funcionalidade entregue.

## 2. Atores

- **Administrador do painel:** acessa as operações autenticadas usando credenciais mantidas na configuração do servidor.
- **Sensor ou integração IoT:** envia leituras de telemetria pela API; os endpoints atuais de telemetria não exigem autenticação.
- **Consumidor ou parceiro:** consulta dados públicos de lote por código.
- **Usuários e administradores cadastrados:** registros mantidos no banco com senha protegida; esses registros não são usados como identidades de login do painel nesta versão.

## 3. Requisitos funcionais

### 3.1 Autenticação e segurança

#### RF-01 — Autenticar o painel

O sistema deve autenticar o acesso administrativo com `ADMIN_USERNAME` e `ADMIN_PASSWORD` configurados fora do código e emitir token Bearer JWT válido por prazo configurado.

#### RF-02 — Proteger rotas internas

As operações internas protegidas devem exigir `Authorization: Bearer <token>` válido. Sem token, a API deve responder `401`.

#### RF-03 — Armazenar segredos fora do repositório

O servidor deve exigir `SECRET_KEY` com ao menos 32 caracteres para assinar e validar JWT. Não deve existir chave de assinatura ou credencial administrativa padrão no código.

#### RF-04 — Proteger senhas cadastradas

Senhas de usuários e administradores cadastrados devem ser armazenadas como hash scrypt, nunca devolvidas pela API e migradas de forma automática quando encontradas em texto puro no banco legado.

### 3.2 Cadastro e gestão

#### RF-05 — Gerenciar cadastros internos

Usuários, administradores, funcionários, clientes e fornecedores devem permitir as operações CRUD expostas por suas rotas autenticadas e validação dos campos por Pydantic.

#### RF-06 — Persistir dados

Os cadastros devem permanecer disponíveis após reinicializações do processo, por meio do SQLite configurado no servidor.

### 3.3 Colmeias, telemetria e produção

#### RF-07 — Gerenciar colmeias

A API deve permitir criação e listagem autenticadas de colmeias.

#### RF-08 — Receber telemetria

A API deve receber leituras contendo `id_colmeia`, `timestamp`, `peso_kg`, `temperatura_c` e `umidade_p`; `bateria_volt` é opcional. Pesos devem ser positivos e a umidade deve estar entre 0 e 100.

#### RF-09 — Consultar histórico

A API deve disponibilizar consulta do histórico de telemetria por `id_colmeia`.

### 3.4 Lotes e rastreabilidade

#### RF-10 — Gerenciar lotes

A API deve permitir cadastrar e consultar internamente lotes por rotas autenticadas.

#### RF-11 — Expor rastreabilidade pública

Uma pessoa sem login deve poder consultar o lote pelo código. A resposta pública deve limitar-se aos dados de rastreabilidade definidos para o consumidor e somente deve ser fornecida quando o lote estiver auditado.

#### RF-12 — Tratar lote indisponível

Lote inexistente ou não auditado deve produzir `404` sem expor detalhes internos.

### 3.5 Catálogo, estoque e vendas

#### RF-13 — Manter catálogo de produtos

O sistema deve permitir cadastrar, listar, editar e excluir produtos com código opcional, nome, categoria, descrição opcional, preço não negativo, unidade e status ativo.

#### RF-14 — Separar catálogo e inventário

O cadastro comercial do produto deve ser armazenado separadamente da quantidade disponível e dos alertas de estoque.

#### RF-15 — Gerenciar estoque

A API deve permitir cadastrar, consultar, atualizar e excluir itens de estoque, além de consultar alertas e relatório do inventário.

#### RF-16 — Registrar vendas

A API deve permitir registrar venda com código, data, valor bruto positivo, tipo e campos opcionais de produto e quantidade.

#### RF-17 — Dividir a receita

Cada venda deve calcular 70% para renda e 30% para o fundo de modernização.

#### RF-18 — Consultar indicadores

A API deve fornecer saldo acumulado, resumo do dashboard e resumo de relatórios para o painel autenticado.

### 3.6 Empresa e interface

#### RF-19 — Manter dados da empresa

A API deve permitir consultar e atualizar o perfil da empresa por rotas autenticadas.

#### RF-20 — Exibir módulos administrativos

O painel deve permitir navegação pelos módulos implementados e oferecer operações de cadastro e tabela onde há formulário conectado à API.

## 4. Requisitos não funcionais

### 4.1 Segurança

- Guardar `.env` fora do controle de versão e gerar segredos aleatórios exclusivos por instalação.
- Usar comparação em tempo constante para credenciais e verificação de hash.
- Nunca incluir senhas nos resultados de listagem, criação ou atualização.
- Restringir acesso administrativo por JWT nas rotas internas.
- Limitar a exposição pública de rastreabilidade ao contrato do consumidor.
- Documentar que CORS não autentica chamadas diretas à API.
- Registrar que as rotas de telemetria estão abertas na implementação atual e devem ficar em rede confiável até receber autenticação apropriada.

### 4.2 Confiabilidade e integridade

- Criar tabelas do SQLite automaticamente na inicialização.
- Preservar identificadores dos registros e serializar datas em ISO 8601.
- Retornar erros de validação como `422`, ausência de autenticação como `401` e lote público indisponível como `404`.
- Não retornar stack trace ao cliente.
- Manter cópia de segurança do arquivo SQLite antes de operações de manutenção.

### 4.3 Manutenibilidade

- Separar rotas, modelos, regras de serviço, autenticação e persistência.
- Validar payloads com Pydantic.
- Manter testes automatizados para API, serviços, persistência e segurança.
- Manter documentação de operação e contratos sincronizada com o OpenAPI implementado.

### 4.4 Limites de capacidade conhecidos

A aplicação não implementa atualmente controle de acesso por papéis, rate limiting, revogação de JWT, logging estruturado, métricas ou tracing centralizado. A validade do token não substitui os controles de autorização por função ainda necessários para implantação multiusuário.

## 5. Regras de negócio e validação

| Domínio | Regra implementada |
|---|---|
| JWT | `SECRET_KEY` obrigatória e com comprimento mínimo de 32 caracteres; token Bearer com validade definida por `ACCESS_TOKEN_EXPIRE_MINUTES`. |
| Login | `ADMIN_USERNAME` e `ADMIN_PASSWORD` configurados no servidor; senha administrativa com pelo menos 12 caracteres; ausência de credenciais retorna `503`. |
| Senhas cadastradas | Hash scrypt individualizado por salt; não incluído nas respostas; dados legados em texto puro migram ao inicializar o banco. |
| Telemetria | `peso_kg > 0`, `0 <= umidade_p <= 100`, timestamp convertido para UTC, bateria opcional. |
| Lote | Criação exige dados de origem e qualidade; a consulta pública limita-se a lote auditado. |
| Produto | Nome obrigatório, preço `>= 0`; código e descrição opcionais; produto independente do estoque. |
| Estoque | Quantidade, mínimo e preço unitário não negativos; item de estoque possui campos e ciclo de vida próprios. |
| Venda | Valor bruto positivo; renda de 70% e fundo de 30%; produto e quantidade opcionais. |

## 6. Matriz de acesso da API

`Protegido` significa exigência de JWT Bearer. `Público` significa que a rota não exige esse token na implementação atual.

| Grupo | Rotas | Acesso |
|---|---|---|
| Saúde e autenticação | `GET /health`, `POST /api/v1/auth/login` | Público |
| Consulta de rastreabilidade | `GET /api/v1/rastreabilidade/{codigo_lote}` | Público |
| Telemetria | `POST /api/v1/telemetria`, `GET /api/v1/telemetria/{id_colmeia}` | Público; limitar a rede confiável |
| Usuários | `GET /api/v1/usuarios`, `POST /api/v1/usuarios/cadastrar`, `PUT/DELETE /api/v1/usuarios/{usuario_id}` | Protegido |
| Administradores | `GET /api/v1/administradores`, `POST /api/v1/administradores/cadastrar`, `PUT/DELETE /api/v1/administradores/{administrador_id}` | Protegido |
| Funcionários | `GET /api/v1/funcionarios`, `POST /api/v1/funcionarios/cadastrar`, `PUT/DELETE /api/v1/funcionarios/{funcionario_id}` | Protegido |
| Clientes | `GET /api/v1/clientes`, `POST /api/v1/clientes/cadastrar`, `PUT/DELETE /api/v1/clientes/{cliente_id}` | Protegido |
| Fornecedores | `GET /api/v1/fornecedores`, `POST /api/v1/fornecedores/cadastrar`, `PUT/DELETE /api/v1/fornecedores/{fornecedor_id}` | Protegido |
| Colmeias | `GET /api/v1/colmeias`, `POST /api/v1/colmeias` | Protegido |
| Lotes | `GET /api/v1/lotes`, `POST /api/v1/lotes`, `GET /api/v1/lotes/{codigo_lote}` | Protegido |
| Produtos | `GET /api/v1/produtos`, `POST /api/v1/produtos/cadastrar`, `PUT/DELETE /api/v1/produtos/{produto_id}` | Protegido |
| Estoque | `GET /api/v1/estoque`, `POST /api/v1/estoque/cadastrar`, `PUT/DELETE /api/v1/estoque/{item_id}`, `GET /api/v1/estoque/alertas`, `GET /api/v1/estoque/relatorio` | Protegido |
| Vendas e financeiro | `GET /api/v1/vendas`, `POST /api/v1/vendas/registrar`, `PUT/DELETE /api/v1/vendas/{venda_id}`, `GET /api/v1/financeiro/fundo-acumulado` | Protegido |
| Indicadores | `GET /api/v1/dashboard/resumo`, `GET /api/v1/relatorios/resumo` | Protegido |
| Empresa | `GET /api/v1/empresa`, `PUT /api/v1/empresa` | Protegido |

## 7. Critérios de aceitação

1. Login configurado retorna JWT; credenciais padrão antigas são rejeitadas.
2. Sem segredo JWT válido, a aplicação não emite nem aceita tokens.
3. Rotas protegidas rejeitam requisições anônimas com `401`.
4. Listagem e atualização de usuários e administradores não retornam o campo `password`.
5. Novas senhas são armazenadas com hash scrypt e verificáveis sem armazenar o texto original.
6. Inicialização converte senhas legadas para hash sem alterar a capacidade de validar a senha original.
7. Telemetria válida é persistida; entradas fora dos limites Pydantic são rejeitadas.
8. Consulta pública retorna apenas dados permitidos para lote auditado; lote não elegível retorna `404`.
9. Produtos são persistidos no catálogo separado da tabela de estoque e permitem CRUD autenticado.
10. Venda válida persiste os valores da divisão 70/30.
11. Toda rota e seu requisito de autenticação pode ser conferida no `/docs` gerado pelo FastAPI.

## 8. Documentos relacionados

- [Visão geral](./01-visao-geral.md)
- [Arquitetura](./03-arquitetura.md)
- [Modelagem e contratos](./04-modelagem-dados-e-api.md)
- [Instalação, execução e segurança operacional](./apiario-rocha-backend/README.md)
