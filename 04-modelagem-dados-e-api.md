# Fase 4 — Modelagem de Dados e Contratos de API

## 1. Objetivo da fase
Esta fase define a estrutura dos dados que serão persistidos no banco SQLite e os contratos de entrada e saída das rotas da API. O foco é garantir consistência entre:
- telemetria das colmeias;
- rastreabilidade dos lotes;
- operação financeira;
- autenticação e acesso às rotas internas.

A modelagem deve ser simples, clara e compatível com FastAPI + Pydantic + aiosqlite, mantendo a linguagem do domínio do apiário e do mel.

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
- _id: identificador técnico do registro;
- codigo_lote: código usado na consulta do lote;
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

### 2.5 Produto
Representa um item comercial do catálogo, sem controlar sua quantidade em estoque.

Atributos principais:
- _id: identificador único;
- codigo: código comercial opcional;
- nome: nome do produto;
- categoria: grupo comercial;
- descricao: descrição opcional;
- preco: preço unitário, maior ou igual a zero;
- unidade: unidade de venda;
- ativo: disponibilidade do produto no catálogo;
- data_cadastro: data de criação do registro.

### 2.6 Fundo de modernização
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

## 4. Estrutura de tabelas no SQLite

O banco é criado automaticamente no arquivo configurado por `SQLITE_PATH` (por padrão, `../data/apiario.db`, fora da pasta pública do backend). O backend cria tabelas para usuários, administradores, funcionários, clientes, fornecedores, vendas, estoque, produtos, colmeias, lotes, telemetria e empresa. Cada tabela usa um identificador textual `_id`; datas são armazenadas em formato ISO 8601 e indicadores booleanos como inteiros. A implementação não declara restrições `UNIQUE` para os códigos comerciais ou de lote; portanto, a unicidade desses campos ainda não é garantida pelo banco.

```text
data/apiario.db
```

### 4.1 Tabela: colmeias
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

### 4.2 Tabela: telemetria
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

### 4.3 Tabela: lotes
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

### 4.4 Tabela: vendas
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

### 4.5 Fundo de modernização
```json
{
  "_id": "fundo_001",
  "periodo": "2026-Q4",
  "valor_acumulado": 18500.00,
  "total_retenido": 18500.00,
  "atualizado_em": "2026-10-20T18:00:00Z"
}
```

### 4.6 Produtos
```json
{
  "_id": "produto_001",
  "codigo": "MEL-500",
  "nome": "Mel silvestre 500g",
  "categoria": "mel",
  "descricao": "Mel silvestre em pote de 500g",
  "preco": 35.5,
  "unidade": "pote",
  "ativo": true,
  "data_cadastro": "2026-10-23T14:00:00Z"
}
```

### 4.7 Estoque
```json
{
  "_id": "estoque_001",
  "produto": "Mel silvestre 500g",
  "categoria": "mel",
  "quantidade": 24,
  "preco_unitario": 35.5,
  "estoque_minimo": 5,
  "unidade": "pote",
  "status": "disponivel",
  "criado_em": "2026-10-23T14:00:00Z",
  "atualizado_em": "2026-10-23T14:00:00Z"
}
```

Produto e estoque são tabelas independentes. O campo `produto` de estoque é texto, não uma chave estrangeira para a tabela `produtos`.

### 4.8 Usuários e administradores
As tabelas de usuários e administradores incluem os campos de credencial, mas senhas são salvas no seguinte formato:

```text
password = $scrypt$<parâmetros>$<salt>$<derivação>
```

O valor armazenado nunca é a senha original. No início da aplicação, valores legados sem o prefixo de hash são migrados para scrypt. As respostas de listagem e atualização removem o campo `password`.

---

## 5. Modelos Pydantic

Os trechos ilustrativos abaixo resumem os contratos. A especificação OpenAPI em `/openapi.json` e os modelos em `src/models/` são a fonte de verdade para os campos disponíveis na versão executada.

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

### 5.6 Produto
```json
{
  "codigo": "MEL-500",
  "nome": "Mel silvestre 500g",
  "categoria": "mel",
  "descricao": "Mel silvestre em pote de 500g",
  "preco": 35.5,
  "unidade": "pote",
  "ativo": true
}
```

Na criação, `nome` e `preco` são obrigatórios. `preco` não pode ser negativo; `codigo`, `descricao` e demais atributos têm valores padrão definidos em `src/models/produto.py`.

### 5.7 Item de estoque
`ItemEstoqueCreate` requer `produto`, `quantidade` e `preco_unitario`. Quantidade, preço e estoque mínimo devem ser não negativos. Categoria, mínimo e unidade têm valores padrão.

### 5.8 Credencial administrativa
```json
{
  "username": "administrador-configurado",
  "password": "senha fornecida no login"
}
```

Esse payload é recebido somente pelo endpoint de login e comparado às configurações do servidor. A aplicação não mantém uma credencial administrativa fixa nem utiliza as senhas das tabelas de usuário/administrador para autenticar o painel nesta versão.

### 5.9 Matriz de campos e validação dos cadastros

As regras abaixo resumem os modelos Pydantic da implementação. Em operações `PUT`, todos os campos são opcionais; campos omitidos permanecem inalterados.

| Modelo | Campos obrigatórios na criação | Campos opcionais, padrões e limites |
|---|---|---|
| Usuário | `nome` não vazio; `email` não vazio; `username` com ao menos 3 caracteres; `password` com ao menos 6 caracteres | `perfil`, padrão `usuario`. |
| Administrador cadastrado | `nome`, `email`; `username` com ao menos 3 caracteres; `password` com ao menos 6 caracteres | `nivel`, padrão `admin`. Essas credenciais não autenticam o painel. |
| Funcionário | `nome`, `email`, `cargo`, `departamento` não vazios; `salario > 0` | `status`, padrão `ativo`; `observacoes`. |
| Cliente | `nome` não vazio | `email`, `telefone`, `documento`, `cidade`, `observacoes`; `tipo`, padrão `pf`. Os campos de texto opcionais informados não podem ser vazios. |
| Fornecedor | `nome` não vazio | `cnpj`, `email`, `telefone`, `categoria`, `cidade`, `observacoes`; texto opcional deve ser não vazio quando enviado. |
| Colmeia | `codigo`, `nome`, `localizacao` não vazios | `status`, padrão `ativa`; `observacoes`. |
| Lote | `codigo_lote`, `variedade_florada`, `data_extracao`, `laboratorio`, `storytelling` não vazios; `quantidade_potes > 0` | `umidade >= 0`, `pureza >= 0`; `auditado`, padrão `true`; `id_colmeia`. |
| Produto | `nome` não vazio; `preco >= 0` | `codigo` opcional; `categoria`, padrão `geral`; `descricao`; `unidade`, padrão `unidade`; `ativo`, padrão `true`. |
| Item de estoque | `produto` não vazio; `quantidade >= 0`; `preco_unitario >= 0` | `categoria`, padrão `geral`; `estoque_minimo`, padrão `0` e não negativo; `unidade`, padrão `unidade`. |
| Venda | `codigo_venda`, `data_venda`, `tipo_venda` não vazios; `valor_bruto > 0` | `produto`; `quantidade > 0`. |
| Empresa | Nenhum campo é obrigatório | Todos os dados de perfil são opcionais; campos não reconhecidos são ignorados pelo modelo. |
| Telemetria | `id_colmeia` não vazio; `timestamp`; `peso_kg > 0`; `temperatura_c`; `0 <= umidade_p <= 100` | `bateria_volt`. |

Os modelos não validam todos os formatos de domínio (por exemplo, CNPJ formal ou sintaxe de email); em vários campos o contrato exige apenas uma string não vazia.

---

## 6. Contratos de API

O prefixo dos endpoints de domínio é `/api/v1`. `Bearer` indica que o cabeçalho `Authorization: Bearer <access_token>` é obrigatório. Os caminhos abaixo correspondem às rotas implementadas; a especificação OpenAPI fornece os schemas completos e atualizados.

### 6.1 POST /api/v1/telemetria
Endpoint público na implementação atual, responsável por receber e persistir dados de sensores. Recomenda-se restringir sua exposição à rede confiável até implementar autenticação para dispositivos.

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

### 6.6 GET /api/v1/dashboard/resumo
Endpoint protegido que fornece os indicadores operacionais consumidos pelo painel.

#### Resposta esperada
```json
{
  "total_vendas": 4,
  "fundo_acumulado": 750.00,
  "total_funcionarios": 5,
  "total_clientes": 3,
  "total_fornecedores": 2,
  "total_colmeias_ativas": 6,
  "total_lotes": 9,
  "total_leituras_telemetria": 24,
  "estoque_total": 18,
  "faturamento_mes": 2500.00
}
```

### 6.7 Catálogo de produtos
As rotas a seguir exigem autenticação:
- `POST /api/v1/produtos/cadastrar`: cadastra produto; exige nome e preço não negativo;
- `GET /api/v1/produtos`: lista produtos;
- `PUT /api/v1/produtos/{produto_id}`: atualiza os campos enviados;
- `DELETE /api/v1/produtos/{produto_id}`: exclui o produto.

`total_colmeias_ativas` considera somente colmeias com status `ativa`; `total_lotes` e `total_leituras_telemetria` representam os respectivos documentos persistidos.

### 6.8 Autenticação — POST /api/v1/auth/login
Rota pública. Recebe credenciais configuradas no servidor; não registra nova conta.

#### Requisição
```json
{
  "username": "administrador-configurado",
  "password": "senha exclusiva configurada localmente"
}
```

#### Resposta de sucesso
Status `200 OK`:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Credenciais inválidas resultam em `401`. Quando `ADMIN_USERNAME` ou `ADMIN_PASSWORD` não está configurado, ou a senha administrativa tem menos de 12 caracteres, o login responde `503`. A chave de assinatura JWT `SECRET_KEY` é verificada ao emitir ou validar tokens e deve ter pelo menos 32 caracteres.

### 6.9 CRUD de cadastros protegidos
Todos os métodos nesta seção exigem Bearer JWT:

| Recurso | Criar | Listar | Atualizar | Excluir |
|---|---|---|---|---|
| Usuários | `POST /api/v1/usuarios/cadastrar` | `GET /api/v1/usuarios` | `PUT /api/v1/usuarios/{usuario_id}` | `DELETE /api/v1/usuarios/{usuario_id}` |
| Administradores | `POST /api/v1/administradores/cadastrar` | `GET /api/v1/administradores` | `PUT /api/v1/administradores/{administrador_id}` | `DELETE /api/v1/administradores/{administrador_id}` |
| Funcionários | `POST /api/v1/funcionarios/cadastrar` | `GET /api/v1/funcionarios` | `PUT /api/v1/funcionarios/{funcionario_id}` | `DELETE /api/v1/funcionarios/{funcionario_id}` |
| Clientes | `POST /api/v1/clientes/cadastrar` | `GET /api/v1/clientes` | `PUT /api/v1/clientes/{cliente_id}` | `DELETE /api/v1/clientes/{cliente_id}` |
| Fornecedores | `POST /api/v1/fornecedores/cadastrar` | `GET /api/v1/fornecedores` | `PUT /api/v1/fornecedores/{fornecedor_id}` | `DELETE /api/v1/fornecedores/{fornecedor_id}` |

Senhas de usuários e administradores são protegidas por hash scrypt. O campo `password` não é incluído nas respostas de listagem ou atualização.

### 6.10 Estoque protegido

- `POST /api/v1/estoque/cadastrar`: cadastra item.
- `GET /api/v1/estoque`: lista itens.
- `GET /api/v1/estoque/alertas`: lista itens no mínimo ou abaixo dele.
- `GET /api/v1/estoque/relatorio`: calcula totais, alertas e valor estimado.
- `PUT /api/v1/estoque/{item_id}` e `DELETE /api/v1/estoque/{item_id}`: atualiza e remove item.

Todos exigem Bearer JWT. O relatório de estoque não representa o catálogo comercial de produtos.

### 6.11 Vendas, financeiro e indicadores protegidos

- `POST /api/v1/vendas/registrar`, `GET /api/v1/vendas`, `PUT /api/v1/vendas/{venda_id}` e `DELETE /api/v1/vendas/{venda_id}`.
- `GET /api/v1/financeiro/fundo-acumulado`.
- `GET /api/v1/dashboard/resumo` e `GET /api/v1/relatorios/resumo`.

Todas exigem Bearer JWT. Campos opcionais `produto` e `quantidade` da venda não são identificadores relacionais para o catálogo. O serviço de venda também pode realizar a baixa de estoque definida nas regras do serviço.

### 6.12 Empresa, colmeias e lotes protegidos

- Empresa: `GET /api/v1/empresa` e `PUT /api/v1/empresa`.
- Colmeias: `GET /api/v1/colmeias` e `POST /api/v1/colmeias`.
- Lotes: `GET /api/v1/lotes`, `POST /api/v1/lotes` e `GET /api/v1/lotes/{codigo_lote}`.

Todos exigem Bearer JWT.

### 6.13 Saúde e rastreabilidade pública

- `GET /health`: público; informa se o processo responde.
- `GET /api/v1/rastreabilidade/{codigo_lote}`: público; retorna os campos públicos de um lote auditado ou `404` caso ele não esteja disponível.

O endpoint de rastreabilidade não devolve registro administrativo completo. Para operações internas de lote, use as rotas protegidas de `/api/v1/lotes`.

---

## 7. Regras de validação e integridade

### 7.1 Telemetria
- `id_colmeia` é obrigatório e não pode ser vazio;
- `timestamp` deve ser uma data reconhecida por Pydantic e é normalizado para UTC pelo serviço;
- `peso_kg` deve ser maior que zero;
- `umidade_p` deve estar entre 0 e 100;
- bateria_volt é opcional;
- dados inválidos devem ser rejeitados por Pydantic.

### 7.2 Rastreabilidade
- `codigo_lote` identifica a consulta, mas a unicidade não é imposta por índice `UNIQUE` na implementação atual;
- lote só pode ser consultado publicamente quando auditado;
- caso o lote não exista ou não esteja auditado, responder 404.

### 7.3 Financeiro
- valor_bruto deve ser maior que zero;
- cálculo da divisão deve seguir 70% e 30%;
- valores devem ser armazenados com arredondamento financeiro adequado;
- rotas de escrita financeira exigem autenticação.

### 7.4 Produtos e credenciais
- `nome` é obrigatório e não vazio; `preco` deve ser maior ou igual a zero;
- cadastro do produto não altera o inventário;
- `SECRET_KEY` com menos de 32 caracteres não pode assinar nem validar tokens;
- a senha administrativa deve possuir pelo menos 12 caracteres;
- senhas cadastradas são derivadas com scrypt, verificadas com comparação em tempo constante e omitidas das respostas;
- a migração de senhas legadas acontece na inicialização da aplicação.

### 7.5 Códigos e relações entre entidades
- `_id` é a chave primária textual de cada tabela;
- o campo `produto` em estoque e vendas é texto livre, não uma chave estrangeira para o catálogo;
- códigos de produto, estoque, venda e lote não têm restrição única declarada pelo banco nesta versão;
- quaisquer relações aparentes entre entidades são convenções da aplicação, salvo quando houver restrição explicitamente configurada no SQLite.

---

## 8. Critérios de aceitação desta fase
1. Todas as entidades do domínio estão identificadas e documentadas.
2. Tabelas SQLite refletem as necessidades de telemetria, rastreabilidade e financeiro.
3. Os modelos Pydantic validam campos obrigatórios e tipos esperados.
4. Os contratos de API definem payloads e respostas de forma clara.
5. A regra 70/30 está formalizada no esquema de cálculo financeiro.
6. A rota pública de lote permanece acessível sem autenticação.
7. A rota financeira exige autenticação e integrações sensíveis ficam protegidas.

---

## 9. Entregáveis da fase
- modelagem conceitual das entidades;
- estrutura de tabelas SQLite;
- modelos Pydantic para entrada e resposta;
- contratos de API definidos;
- regras de validação e integridade;
- base para implementação das rotas e serviços.

## 10. Status da fase
Status: contratos documentados com base na implementação atual.

Consulte o `/openapi.json` da instância em execução para obter schemas e rotas gerados diretamente pelos modelos e roteadores instalados. As diferenças entre contrato atual, requisitos futuros e telas do painel são apontadas neste documento e no [README operacional](./apiario-rocha-backend/README.md).
