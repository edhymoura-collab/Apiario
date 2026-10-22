# Fase 4 — Modelagem de Dados e Contratos de API

## 1. Objetivo da fase
Esta fase define a estrutura dos dados que serão persistidos no banco MongoDB e os contratos de entrada e saída das rotas da API. O foco é garantir consistência entre:
- telemetria das colmeias;
- rastreabilidade dos lotes;
- operação financeira;
- autenticação e acesso às rotas internas.

A modelagem deve ser simples, clara e compatível com FastAPI + Pydantic + Motor, mantendo a linguagem do domínio do apiário e do mel.

---

## 2. Entidades do domínio

### 2.1 Colmeia
Representa cada unidade produtiva do apiário.

Atributos principais:
- id_colmeia: identificador único da colmeia;
- codigo: código interno ou identificador operacional;
- nome: nome amigável da colmeia;
- localizacao: apiário, setor ou área geográfica;
- status: ativa, inativa, manutenção, sem sinal;
- data_cadastro: data de criação do registro;
- observacoes: informações complementares.

### 2.2 Leitura de telemetria
Representa cada leitura de sensores de uma colmeia.

Atributos principais:
- id_leitura: identificador único;
- id_colmeia: referência à colmeia;
- timestamp_utc: momento da leitura em UTC;
- peso_kg: peso da colmeia em quilogramas;
- temperatura_c: temperatura ambiente/interna;
- umidade_p: umidade relativa do ambiente;
- bateria_volt: nível da bateria do sensor (opcional);
- criado_em: data do registro no sistema.

### 2.3 Lote de rastreabilidade
Representa um lote de mel ou produção rastreável.

Atributos principais:
- codigo_lote: código único do lote;
- id_colmeia: colmeia de origem ou agrupamento produtivo;
- variedade_florada: origem floral do mel;
- data_extracao: data da extração;
- umidade: percentual de umidade;
- pureza: percentual de pureza ou índice de qualidade;
- quantidade_potes: volume de embalagens;
- laboratorio: nome do laboratório ou análise;
- storytelling: texto descritivo para consumidor;
- auditado: indica se o lote foi validado;
- criado_em: data de inserção.

### 2.4 Venda
Representa uma operação comercial vinculada ao produto.

Atributos principais:
- id_venda: identificador da venda;
- codigo_venda: código externo ou interno da transação;
- data_venda: data da operação;
- valor_bruto: valor total da venda;
- valor_renda: parcela da renda familiar;
- valor_fundo: parcela destinada ao fundo de modernização;
- tipo_venda: B2B, cooperativa ou canal direto;
- status: pendente, confirmada ou cancelada.

### 2.5 Fundo de modernização
Representa o montante acumulado por retenção financeira.

Atributos principais:
- id_fundo: identificador do registro;
- periodo: mês, trimestre ou ano de referência;
- valor_acumulado: saldo do fundo;
- total_retenido: soma total monetária retida;
- atualizado_em: data da última atualização.

---

## 3. Relacionamentos principais

### 3.1 Colmeia e telemetria
Uma colmeia pode ter várias leituras de telemetria ao longo do tempo. A relação é de 1:N.

### 3.2 Colmeia e lote
Um lote pode estar associado a uma ou mais colmeias, dependendo do processo de produção e agrupamento. A modelagem inicial pode tratar como 1:N, com vínculo opcional por colmeia principal.

### 3.3 Venda e fundo
Cada venda gera um impacto financeiro no saldo do fundo, em conformidade com a regra 70/30.

---

## 4. Estrutura sugerida de coleções no MongoDB

```text
apiario_rocha_db/
├── colmeias/
├── telemetria/
├── lotes/
├── vendas/
├── fundos_modernizacao/
└── usuarios/
```

### 4.1 Coleção: colmeias
```json
{
  "_id": "colmeia_001",
  "codigo": "C-001",
  "nome": "Colmeia Norte 01",
  "localizacao": "Setor A",
  "status": "ativa",
  "data_cadastro": "2026-10-01T08:00:00Z",
  "observacoes": "Colmeia monitorada por sensor IoT"
}
```

### 4.2 Coleção: telemetria
```json
{
  "_id": "leit_001",
  "id_colmeia": "colmeia_001",
  "timestamp_utc": "2026-10-20T14:35:00Z",
  "peso_kg": 18.4,
  "temperatura_c": 31.2,
  "umidade_p": 62,
  "bateria_volt": 12.7,
  "criado_em": "2026-10-20T14:36:00Z"
}
```

### 4.3 Coleção: lotes
```json
{
  "_id": "lote_001",
  "codigo_lote": "LOT-2026-001",
  "id_colmeia": "colmeia_001",
  "variedade_florada": "Eucalipto",
  "data_extracao": "2026-10-18",
  "umidade": 17.5,
  "pureza": 98.2,
  "quantidade_potes": 120,
  "laboratorio": "Laboratório de Qualidade Apiário Rocha",
  "storytelling": "Mel floral de origem eucalipto com aroma suave e brilho intenso.",
  "auditado": true,
  "criado_em": "2026-10-18T18:00:00Z"
}
```

### 4.4 Coleção: vendas
```json
{
  "_id": "venda_001",
  "codigo_venda": "VEN-2026-1001",
  "data_venda": "2026-10-20",
  "valor_bruto": 2500.00,
  "valor_renda": 1750.00,
  "valor_fundo": 750.00,
  "tipo_venda": "cooperativa",
  "status": "confirmada"
}
```

### 4.5 Coleção: fundos_modernizacao
```json
{
  "_id": "fundo_001",
  "periodo": "2026-Q4",
  "valor_acumulado": 18500.00,
  "total_retenido": 18500.00,
  "atualizado_em": "2026-10-20T18:00:00Z"
}
```

---

## 5. Modelos Pydantic

### 5.1 Modelo de telemetria de entrada
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TelemetriaCreate(BaseModel):
    id_colmeia: str = Field(..., min_length=1)
    timestamp: datetime
    peso_kg: float = Field(..., gt=0)
    temperatura_c: float
    umidade_p: float = Field(..., ge=0, le=100)
    bateria_volt: Optional[float] = None
```

### 5.2 Modelo de resposta de telemetria
```python
class TelemetriaResponse(BaseModel):
    id_leitura: str
    id_colmeia: str
    timestamp_utc: datetime
    peso_kg: float
    temperatura_c: float
    umidade_p: float
    bateria_volt: Optional[float]
    criado_em: datetime
```

### 5.3 Modelo de lote público
```python
class LotePublico(BaseModel):
    codigo_lote: str
    variedade_florada: str
    data_extracao: str
    umidade: float
    pureza: float
    quantidade_potes: int
    laboratorio: str
    storytelling: str
```

### 5.4 Modelo de venda
```python
class VendaCreate(BaseModel):
    codigo_venda: str
    data_venda: str
    valor_bruto: float = Field(..., gt=0)
    tipo_venda: str
```

### 5.5 Modelo para cálculo financeiro
```python
class DivisaoFinanceira(BaseModel):
    valor_bruto: float
    percentual_renda: float = 70.0
    percentual_fundo: float = 30.0

    @property
    def valor_renda(self) -> float:
        return self.valor_bruto * (self.percentual_renda / 100)

    @property
    def valor_fundo(self) -> float:
        return self.valor_bruto * (self.percentual_fundo / 100)
```

---

## 6. Contratos de API

### 6.1 POST /api/v1/telemetria
Endpoint responsável por receber e persistir dados de sensores.

#### Requisição
```json
{
  "id_colmeia": "colmeia_001",
  "timestamp": "2026-10-20T14:35:00Z",
  "peso_kg": 18.4,
  "temperatura_c": 31.2,
  "umidade_p": 62,
  "bateria_volt": 12.7
}
```

#### Resposta de sucesso
- Status: 201 Created

```json
{
  "message": "Leitura de telemetria registrada com sucesso",
  "data": {
    "id_colmeia": "colmeia_001",
    "timestamp_utc": "2026-10-20T14:35:00Z",
    "peso_kg": 18.4,
    "temperatura_c": 31.2,
    "umidade_p": 62,
    "bateria_volt": 12.7
  }
}
```

### 6.2 GET /api/v1/telemetria/{id_colmeia}
Endpoint para consultar histórico por colmeia.

#### Resposta esperada
```json
{
  "id_colmeia": "colmeia_001",
  "historico": [
    {
      "timestamp_utc": "2026-10-20T14:35:00Z",
      "peso_kg": 18.4,
      "temperatura_c": 31.2,
      "umidade_p": 62
    }
  ]
}
```

### 6.3 GET /api/v1/rastreabilidade/{codigo_lote}
Endpoint público para consulta de lote, sem autenticação.

#### Resposta esperada
```json
{
  "codigo_lote": "LOT-2026-001",
  "variedade_florada": "Eucalipto",
  "data_extracao": "2026-10-18",
  "umidade": 17.5,
  "pureza": 98.2,
  "quantidade_potes": 120,
  "laboratorio": "Laboratório de Qualidade Apiário Rocha",
  "storytelling": "Mel floral de origem eucalipto com aroma suave e brilho intenso."
}
```

#### Resposta para lote inexistente
- Status: 404 Not Found

```json
{
  "detail": "Lote não encontrado"
}
```

### 6.4 POST /api/v1/vendas/registrar
Endpoint protegido com autenticação.

#### Requisição
```json
{
  "codigo_venda": "VEN-2026-1001",
  "data_venda": "2026-10-20",
  "valor_bruto": 2500.00,
  "tipo_venda": "cooperativa"
}
```

#### Resposta de sucesso
```json
{
  "message": "Venda registrada com sucesso",
  "valor_bruto": 2500.00,
  "valor_renda": 1750.00,
  "valor_fundo": 750.00,
  "tipo_venda": "cooperativa"
}
```

### 6.5 GET /api/v1/financeiro/fundo-acumulado
Endpoint protegido para consulta do saldo do fundo.

#### Resposta esperada
```json
{
  "valor_acumulado": 18500.00,
  "periodo": "2026-Q4",
  "updated_at": "2026-10-20T18:00:00Z"
}
```

---

## 7. Regras de validação e integridade

### 7.1 Telemetria
- campo id_colmeia é obrigatório;
- timestamp deve ser em UTC;
- peso_kg deve ser maior que zero;
- umidade_p deve estar entre 0 e 100;
- bateria_volt é opcional;
- dados inválidos devem ser rejeitados por Pydantic.

### 7.2 Rastreabilidade
- codigo_lote deve ser único;
- lote só pode ser consultado publicamente quando auditado;
- caso o lote não exista ou não esteja auditado, responder 404.

### 7.3 Financeiro
- valor_bruto deve ser maior que zero;
- cálculo da divisão deve seguir 70% e 30%;
- valores devem ser armazenados com arredondamento financeiro adequado;
- rotas de escrita financeira exigem autenticação.

---

## 8. Critérios de aceitação desta fase
1. Todas as entidades do domínio estão identificadas e documentadas.
2. Coleções de MongoDB refletem as necessidades de telemetria, rastreabilidade e financeiro.
3. Os modelos Pydantic validam campos obrigatórios e tipos esperados.
4. Os contratos de API definem payloads e respostas de forma clara.
5. A regra 70/30 está formalizada no esquema de cálculo financeiro.
6. A rota pública de lote permanece acessível sem autenticação.
7. A rota financeira exige autenticação e integrações sensíveis ficam protegidas.

---

## 9. Entregáveis da fase
- modelagem conceitual das entidades;
- estrutura de coleções do MongoDB;
- modelos Pydantic para entrada e resposta;
- contratos de API definidos;
- regras de validação e integridade;
- base para implementação das rotas e serviços.

## 10. Status da fase
Status: concluída para revisão.

> Próxima fase: implementação das rotas, serviços e autenticação.

---

Se aprovar esta fase, eu sigo imediatamente para a implementação real do backend em FastAPI, começando pelas rotas e serviços.
