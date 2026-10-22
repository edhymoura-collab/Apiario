# Fase 1 — Visão Geral da Solução

## 1. Contexto do projeto
A solução Apiário Rocha 4.0 foi concebida para atender a gestão digital de um apiário com foco em:
- monitoramento de colmeias por IoT;
- rastreabilidade do produto até o consumidor final;
- controle financeiro e de fundo de modernização;
- suporte à decisão com base em dados de produção e saúde das colmeias.

O sistema tem como objetivo centralizar dados operacionais, financeiros e de produção em uma API REST robusta e escalável, permitindo integração com sensores, dashboard interno e QR Code de rastreabilidade.

## 2. Objetivo da solução
A plataforma deve permitir:
- receber dados de telemetria de colmeias em tempo real;
- consultar histórico de desempenho e saúde das colmeias;
- fornecer dados de lote e rastreabilidade para o consumidor;
- registrar vendas e automatizar a regra de divisão financeira;
- acompanhar o fundo de modernização para planejamento estratégico.

## 3. Escopo funcional
### 3.1 Módulo de IoT e produção
- coleta de dados de sensores instalados nas colmeias;
- armazenamento de peso, temperatura, umidade e nível de bateria;
- consulta por colmeia e histórico de monitoração.

### 3.2 Módulo de rastreabilidade
- geração e consulta de lote de produção;
- associação de dados de qualidade e pureza;
- exposição pública de informações via QR Code.

### 3.3 Módulo financeiro
- registro de faturamento bruto;
- cálculo automático de renda e fundo de modernização;
- acompanhamento do saldo acumulado do fundo.

## 4. Usuários e perfis
### 4.1 Usuário interno
- gestor do apiário;
- responsável por produção e qualidade;
- área financeira e comercial.

### 4.2 Usuário externo
- consumidor final que acessa informações via QR Code;
- parceiros e cooperativas que consultam dados de lotes e procedência.

## 5. Premissas técnicas
- linguagem principal: Python 3.11+;
- framework: FastAPI;
- banco de dados: MongoDB via Motor;
- modelos validados com Pydantic;
- arquitetura orientada a APIs e módulos funcionais.

## 6. Regras de negócio principais
- O sistema deve registrar telemetria com timestamp em UTC;
- os dados financeiros devem obedecer à divisão 70/30;
- a rota pública de QR Code deve permanecer acessível sem autenticação;
- as rotas de escrita financeira e comercial devem exigir autenticação;
- erros internos devem ser tratados sem expor stack trace ao cliente.

## 7. Entregáveis esperados da fase
- visão clara do problema e da solução;
- definição de escopo funcional;
- alinhamento da arquitetura e dos usuários;
- base para as próximas fases de requisitos e implementação.

## 8. Status da fase
Status: concluída para revisão.

> Próxima fase: requisitos funcionais e não funcionais.

---

Se aprovar esta fase, sigo imediatamente para a criação da Fase 2 em um arquivo separado.
