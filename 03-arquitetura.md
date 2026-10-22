# Fase 3 — Arquitetura Técnica da Solução

## 1. Objetivo da arquitetura
A arquitetura da solução Apiário Rocha 4.0 foi definida para suportar um backend em Python com FastAPI, integrado ao MongoDB via Motor, com foco em:
- ingestão de dados IoT de colmeias;
- consulta de históricos e apoio à decisão;
- rastreabilidade pública do lote;
- registro financeiro com divisão 70/30;
- observabilidade e segurança para endpoints internos.

A proposta é manter uma arquitetura simples, modular e escalável, sem excesso de camadas desnecessárias, mas com separação adequada entre regras de negócio, modelos e acesso a dados.

---

## 2. Visão geral da solução
A solução será composta por:
- API REST em FastAPI;
- modelos baseados em Pydantic;
- conexão com MongoDB via Motor;
- módulos separados por responsabilidade;
- logs estruturados para monitoramento;
- autenticação em endpoints sensíveis.

## 3. Arquitetura lógica

### 3.1 Camadas principais
1. Camada de apresentação
   - endpoints REST expostos pela API;
   - documentação automática via Swagger/OpenAPI do FastAPI.

2. Camada de domínio
   - regras de negócio;
   - cálculo financeiro;
   - validação de dados da telemetria e lote;
   - regras de autenticação e autorização.

3. Camada de acesso a dados
   - integração com banco MongoDB;
   - operações de leitura e escrita;
   - persistência de telemetria, vendas e lotes.

4. Camada de infraestrutura
   - logging;
   - configs de ambiente;
   - segurança de credenciais;
   - integração futura com AWS e observabilidade.

---

## 4. Estrutura de diretórios sugerida

```text
apiario-rocha-backend/
├── .github/
│   └── workflows/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── telemetria.py
│   │   ├── lote.py
│   │   └── financeiro.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── telemetria.py
│   │   ├── rastreabilidade.py
│   │   └── financeiro.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── telemetria_service.py
│   │   ├── rastreabilidade_service.py
│   │   └── financeiro_service.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── security.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py
│   └── main.py
├── .gitignore
├── requirements.txt
├── README.md
└── .env.example
```

## 5. Componentes técnicos

### 5.1 FastAPI
O FastAPI será responsável por:
- expor rotas HTTP;
- receber payloads JSON;
- validar entrada com Pydantic;
- empregar documentação automática em Swagger UI.

### 5.2 Pydantic
Pydantic será usado para:
- modelar os dados de sensor, lote e financeiro;
- validar tipos e campos obrigatórios;
- reduzir erros de entrada na camada de API.

### 5.3 MongoDB + Motor
O MongoDB será utilizado como base principal para persistência das coleções:
- telemetria;
- lotes;
- vendas;
- registros financeiros.

Motor será usado por sua compatibilidade assíncrona com Python e FastAPI.

### 5.4 Segurança
A autenticação será implementada em endpoints sensíveis, com:
- header Authorization: Bearer <token>;
- ou API Key em header personalizado;
- validação centralizada em módulo de segurança.

### 5.5 Logging
A aplicação deve registrar:
- requests importantes;
- payloads de telemetria recebidos;
- erros de banco;
- falhas de autenticação.

Esses logs devem ser capturados em terminal do VS Code e preparados para exportação para soluções de observabilidade, como CloudWatch ou equivalente.

---

## 6. Fluxo de funcionamento

### 6.1 Fluxo de telemetria
1. módulo IoT envia payload HTTP para /api/v1/telemetria;
2. FastAPI valida os campos recebidos;
3. dados são convertidos ao modelo Pydantic;
4. serviço persiste leitura no MongoDB;
5. log registra a operação com sucesso;
6. resposta 201 Created é retornada.

### 6.2 Fluxo de rastreabilidade
1. cliente escaneia QR Code;
2. API recebe codigo_lote pela rota pública;
3. sistema consulta o lote no banco;
4. se existir, retorna os dados públicos;
5. se não existir, responde 404.

### 6.3 Fluxo financeiro
1. vendedor ou sistema interno envia registro de venda;
2. API valida autenticação;
3. serviço divide o valor em 70% e 30%;
4. registros são persistidos no MongoDB;
5. saldo acumulado é consultado pela rota financeira;
6. resposta é retornada ao cliente autorizado.

---

## 7. Regras de integração

### 7.1 Banco de dados
- usar MongoDB com collections específicas;
- persistir dados em formato JSON-like;
- manter identificadores únicos para lote, colmeia e venda.

### 7.2 Ambiente
- usar variáveis de ambiente para credenciais;
- armazenar valores sensíveis em .env local;
- garantir que .env fique no .gitignore.

### 7.3 Tratamento de erros
- falha de conexão com MongoDB deve retornar resposta amigável;
- erros devem ser convertidos em JSON padronizado;
- stack trace não deve ser devolvido ao cliente.

---

## 8. Considerações de escalabilidade
A arquitetura está preparada para evoluir com:
- aumento de sensores IoT;
- maior volume de lotes e rastreabilidade;
- novas rotas do painel administrativo;
- integrações com analytics e IA;
- crescimento de dados financeiros e relatórios.

Para esse nível de crescimento, a arquitetura pode evoluir em etapas futuras para:
- camada de serviços mais especializada;
- cache para consultas frequentes;
- filas assíncronas para ingestão de sensores;
- observabilidade centralizada.

---

## 9. Entregáveis da fase
- arquitetura da solução definida;
- separação por módulos e responsabilidades;
- fluxo de funcionamento mapeado;
- base estrutural para implementação backend.

## 10. Status da fase
Status: concluída para revisão.

> Próxima fase: modelagem de dados e contratos de API.

---

Se aprovar esta fase, eu sigo imediatamente para a Fase 4 em um arquivo separado.
