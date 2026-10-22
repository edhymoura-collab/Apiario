# Fase 2 — Requisitos do Sistema Apiário Rocha 4.0

## 1. Visão geral dos requisitos
Esta fase detalha os requisitos funcionais e não funcionais da solução backend do sistema Apiário Rocha 4.0, com base na especificação técnica já definida para a API REST de gestão, ingestão IoT e rastreabilidade.

O sistema deve suportar três pilares principais:
1. Monitoramento operacional de colmeias por sensores IoT;
2. Rastreabilidade do mel e dados de lote para o consumidor final;
3. Gestão financeira com regra de 70/30 e acompanhamento do fundo de modernização.

---

## 2. Requisitos funcionais

### 2.1 Módulo de telemetria e IoT
#### RF-01 — Receber dados de colmeia
O sistema deve receber payloads com dados de colmeia enviados por dispositivos IoT.

Campos obrigatórios:
- id_colmeia
- timestamp
- peso_kg
- temperatura_c
- umidade_p

Campos opcionais:
- bateria_volt

#### RF-02 — Persistir histórico de leitura
Os dados devem ser armazenados em banco NoSQL com histórico por colmeia, permitindo consultas futuras.

#### RF-03 — Consultar histórico por colmeia
O sistema deve disponibilizar uma rota para retornar o histórico de uma colmeia específica.

#### RF-04 — Validar dados de entrada
Toda leitura recebida deve passar pela validação de tipos, campos obrigatórios e formatação dos valores.

### 2.2 Módulo de rastreabilidade
#### RF-05 — Consultar lote por código
O sistema deve permitir consultar um lote de rastreabilidade pelo código do lote.

#### RF-06 — Exibir dados públicos do lote
A rota pública deve devolver as informações do lote para o consumidor final, incluindo:
- variedade da florada;
- data de extração;
- umidade;
- pureza;
- quantidade de potes;
- informações de laboratório e storytelling.

#### RF-07 — Tratar lote não encontrado
Quando o código informado não existir ou não estiver auditado, a API deve responder com status 404, sem expor detalhes internos.

### 2.3 Módulo financeiro
#### RF-08 — Registrar venda
O sistema deve registrar uma venda B2B ou cooperativa, incluindo valor bruto e data da operação.

#### RF-09 — Dividir renda e fundo
A regra financeira deve dividir automaticamente:
- 70% para renda familiar / faturamento;
- 30% para fundo de modernização / retenção.

#### RF-10 — Consultar saldo acumulado
A API deve retornar o saldo acumulado do fundo de modernização para acompanhamento da meta quadrienal.

#### RF-11 — Requerer autenticação em rotas sensíveis
Rotas de vendas e registros financeiros devem exigir autenticação com API Key ou JWT.

---

## 3. Requisitos não funcionais

### 3.1 Performance
- o sistema deve responder rapidamente às consultas de rastreabilidade;
- as leituras de telemetria devem ser processadas com baixo tempo de resposta;
- a API deve suportar volume crescente de sensores e consultas.

### 3.2 Segurança
- proteger rotas de escrita financeira com autenticação;
- manter a rota pública de QR Code sem autenticação;
- não expor stack trace em respostas de erro;
- armazenar credenciais fora do repositório e respeitar .gitignore.

### 3.3 Confiabilidade
- erro de banco deve ser tratado com resposta HTTP 500 amigável em JSON;
- logs devem registrar payloads processados com sucesso;
- falhas de serviço devem ser observáveis e rastreáveis.

### 3.4 Manutenibilidade
- organização por módulos: config, models, routes;
- uso de Pydantic para validação de dados;
- uso de FastAPI para rotas e documentação automática;
- estrutura de código compatível com manutenção e escalabilidade.

---

## 4. Regras de negócio

### 4.1 Regra da telemetria
- timestamp deve ser registrado em UTC;
- peso, temperatura e umidade são obrigatórios;
- bateria pode ser opcional.

### 4.2 Regra da rastreabilidade
- o lote deve possuir código único;
- informações do lote devem ser públicas quando auditadas;
- lotes não auditados devem ser recusados com resposta 404.

### 4.3 Regra financeira
- faturamento bruto deve ser convertido para percentual de renda e fundo;
- cálculo deve seguir exatamente a regra: 70% e 30%;
- saldo acumulado deve refletir a soma dos valores retidos no período.

### 4.4 Regra de segurança
- rotas de escrita devem exigir cabeçalho Authorization com Bearer token ou API key;
- ausência de autenticação em endpoints financeiros deve ser bloqueada;
- logs de leitura IoT devem ser registráveis pelo sistema sem expor dados sensíveis.

---

## 5. Endpoints esperados

### 5.1 Telemetria
- POST /api/v1/telemetria
- GET /api/v1/telemetria/{id_colmeia}

### 5.2 Rastreabilidade
- GET /api/v1/rastreabilidade/{codigo_lote}

### 5.3 Gestão financeira
- POST /api/v1/vendas/registrar
- GET /api/v1/financeiro/fundo-acumulado

---

## 6. Critérios de aceitação
1. A API responde com status 201 em registros válidos de telemetria.
2. A API retorna histórico por colmeia com base no id informado.
3. A consulta de lote público devolve os dados esperados do lote válido.
4. A consulta de lote inválido retorna 404.
5. A rota financeira exige autenticação.
6. O cálculo financeiro gera corretamente 70% e 30%.
7. Em caso de falha do banco, a API responde com erro amigável em JSON.
8. Logs de payload de IoT são registrados no terminal e em estrutura observável.

## 7. Entregáveis da fase
- requisitos funcionais consolidados;
- requisitos não funcionais definidos;
- regras de negócio documentadas;
- critérios de aceitação para desenvolvimento e validação.

## 8. Status da fase
Status: concluída para revisão.

> Próxima fase: arquitetura técnica e estrutura do backend.

---

Se aprovar esta fase, eu sigo imediatamente para a Fase 3 em um arquivo separado.
