# Fase 1 — Visão Geral da Solução

## 1. Identificação

- **Projeto:** Apiário Rocha 4.0
- **Tipo:** aplicação web de gestão com API REST
- **Interface:** HTML, CSS e JavaScript servidos pelo backend
- **Backend:** Python 3.11+, FastAPI e Pydantic
- **Persistência:** SQLite acessado com aiosqlite
- **Documentação da API:** OpenAPI/Swagger em `/docs`

## 2. Contexto e objetivo

A solução centraliza informações operacionais, comerciais e financeiras de um apiário. Seu objetivo é apoiar a gestão das colmeias e da produção, manter um catálogo comercial independente do inventário, registrar clientes, fornecedores e vendas e oferecer informações públicas de rastreabilidade dos lotes.

O sistema atende dois contextos de acesso:

1. **Operação interna:** painel administrativo protegido por autenticação, destinado à gestão dos cadastros e às consultas operacionais.
2. **Consulta pública:** leitura de informações de um lote auditado por código, destinada ao consumidor ou parceiro que consulta a procedência do produto.

## 3. Escopo funcional

### 3.1 Cadastros e administração

- usuários e administradores;
- funcionários;
- clientes e fornecedores;
- perfil e configurações da empresa.

Os cadastros de usuário e administrador armazenam senha com hash scrypt. Esses registros não são, por si, as credenciais usadas no login administrativo: a autenticação do painel é configurada por variáveis de ambiente.

### 3.2 Catálogo comercial e estoque

- catálogo de produtos com código opcional, categoria, descrição, preço, unidade e status;
- inventário separado, com quantidade, preço unitário, quantidade mínima e alertas;
- registro de vendas com produto e quantidade opcionais.

O catálogo descreve o que pode ser vendido. O estoque controla quantas unidades estão disponíveis; cadastrar um produto não cria automaticamente um item de inventário.

### 3.3 Produção, IoT e rastreabilidade

- cadastro e consulta de colmeias;
- recebimento de leituras de peso, temperatura, umidade e bateria;
- cadastro e consulta interna de lotes;
- consulta pública de dados de um lote auditado.

As rotas de API para colmeias, lotes, telemetria e rastreabilidade existem. Algumas dessas áreas são representadas por telas informativas no painel e não por formulários de operação completos.

### 3.4 Vendas e finanças

- registro de vendas;
- cálculo da divisão financeira de 70% para renda e 30% para fundo;
- consulta do fundo acumulado;
- consulta de resumo operacional e de relatórios.

## 4. Perfis de acesso e limites atuais

- O painel usa credenciais administrativas configuradas em `ADMIN_USERNAME` e `ADMIN_PASSWORD`.
- A API emite JWT assinado com `SECRET_KEY`, com validade configurável.
- Rotas protegidas exigem `Authorization: Bearer <token>`.
- A implementação valida identidade autenticada, mas ainda **não implementa autorização por papel ou permissões granulares**. Um token válido tem o mesmo nível de acesso nas rotas protegidas.
- As rotas de telemetria e rastreabilidade pública não exigem token; seus controles e limites são detalhados na [documentação de requisitos](./02-requisitos.md).

## 5. Regras de negócio principais

- Leituras de telemetria são normalizadas para UTC pelo serviço.
- Umidade da telemetria deve ficar entre 0 e 100; o peso deve ser maior que zero.
- Apenas lotes auditados são apresentados pela rota pública de rastreabilidade.
- O registro de venda calcula 70% para renda e 30% para fundo.
- Produtos e estoque são entidades separadas.
- Senhas cadastradas não são retornadas por endpoints de listagem ou atualização.
- O arquivo `.env` contém segredos locais e não deve ser versionado.

## 6. Premissas e persistência

- O arquivo de banco padrão é `../data/apiario.db`, relativo à pasta do backend.
- A API cria as tabelas na inicialização e migra para hash scrypt as senhas em texto puro encontradas nos cadastros antigos.
- Os dados de amostra de colmeias e lotes são criados apenas quando as respectivas tabelas estão vazias.
- A cópia de segurança do arquivo SQLite é responsabilidade operacional de quem mantém a instalação.

## 7. Documentos relacionados

- [Requisitos funcionais e não funcionais](./02-requisitos.md)
- [Arquitetura da aplicação](./03-arquitetura.md)
- [Modelagem de dados e contratos da API](./04-modelagem-dados-e-api.md)
- [Instalação e operação do backend](./apiario-rocha-backend/README.md)

## 8. Status

O escopo acima descreve o estado implementado da aplicação e registra explicitamente as limitações entre a API e as telas do painel. Requisitos planejados não devem ser interpretados como funcionalidades entregues sem validação no código e nos testes.
