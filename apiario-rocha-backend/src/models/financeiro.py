from pydantic import BaseModel, Field


class VendaCreate(BaseModel):
    codigo_venda: str = Field(..., min_length=1)
    data_venda: str = Field(..., min_length=1)
    valor_bruto: float = Field(..., gt=0)
    tipo_venda: str = Field(..., min_length=1)
    produto: str | None = Field(default=None, min_length=1)
    quantidade: int | None = Field(default=None, gt=0)


class VendaUpdate(BaseModel):
    codigo_venda: str | None = Field(default=None, min_length=1)
    data_venda: str | None = Field(default=None, min_length=1)
    valor_bruto: float | None = Field(default=None, gt=0)
    tipo_venda: str | None = Field(default=None, min_length=1)
    produto: str | None = Field(default=None, min_length=1)
    quantidade: int | None = Field(default=None, gt=0)


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
