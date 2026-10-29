from pydantic import BaseModel, Field


class ItemEstoqueCreate(BaseModel):
    produto: str = Field(..., min_length=1)
    categoria: str = Field(default="geral", min_length=1)
    quantidade: int = Field(..., ge=0)
    preco_unitario: float = Field(..., ge=0)
    estoque_minimo: int = Field(default=0, ge=0)
    unidade: str = Field(default="unidade", min_length=1)


class ItemEstoqueUpdate(BaseModel):
    produto: str | None = Field(default=None, min_length=1)
    categoria: str | None = Field(default=None, min_length=1)
    quantidade: int | None = Field(default=None, ge=0)
    preco_unitario: float | None = Field(default=None, ge=0)
    estoque_minimo: int | None = Field(default=None, ge=0)
    unidade: str | None = Field(default=None, min_length=1)
