from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


FormaPagamento = Literal[
    "pix",
    "dinheiro",
    "cartao_credito",
    "cartao_debito",
    "transferencia",
    "boleto",
    "outro",
    "nao_informado",
]

FormaPagamentoMovimentacao = Literal[
    "pix",
    "dinheiro",
    "cartao_credito",
    "cartao_debito",
    "transferencia",
    "boleto",
    "outro",
]


class VendaCreate(BaseModel):
    codigo_venda: str = Field(..., min_length=1)
    data_venda: str = Field(..., min_length=1)
    valor_bruto: float = Field(..., gt=0)
    tipo_venda: str = Field(..., min_length=1)
    forma_pagamento: FormaPagamento = "nao_informado"
    produto: str | None = Field(default=None, min_length=1)
    quantidade: int | None = Field(default=None, gt=0)


class VendaUpdate(BaseModel):
    codigo_venda: str | None = Field(default=None, min_length=1)
    data_venda: str | None = Field(default=None, min_length=1)
    valor_bruto: float | None = Field(default=None, gt=0)
    tipo_venda: str | None = Field(default=None, min_length=1)
    forma_pagamento: FormaPagamento | None = None
    produto: str | None = Field(default=None, min_length=1)
    quantidade: int | None = Field(default=None, gt=0)


class MovimentacaoFinanceiraCreate(BaseModel):
    tipo: Literal["entrada", "saida"]
    descricao: str = Field(..., min_length=1, max_length=160)
    categoria: str = Field(..., min_length=1, max_length=80)
    valor: float = Field(..., gt=0)
    data_movimentacao: date
    forma_pagamento: FormaPagamentoMovimentacao
    status: Literal["realizada", "pendente"] = "realizada"


class MovimentacaoFinanceiraUpdate(BaseModel):
    tipo: Literal["entrada", "saida"] | None = None
    descricao: str | None = Field(default=None, min_length=1, max_length=160)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    valor: float | None = Field(default=None, gt=0)
    data_movimentacao: date | None = None
    forma_pagamento: FormaPagamentoMovimentacao | None = None
    status: Literal["realizada", "pendente"] | None = None


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


class FundoAcumulado(BaseModel):
    valor_acumulado: float
    periodo: str
    updated_at: str
