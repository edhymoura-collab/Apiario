from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    codigo: str | None = Field(default=None, min_length=1)
    categoria: str = Field(default="geral", min_length=1)
    descricao: str | None = None
    preco: float = Field(..., ge=0)
    unidade: str = Field(default="unidade", min_length=1)
    ativo: bool = True


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    codigo: str | None = Field(default=None, min_length=1)
    categoria: str | None = Field(default=None, min_length=1)
    descricao: str | None = None
    preco: float | None = Field(default=None, ge=0)
    unidade: str | None = Field(default=None, min_length=1)
    ativo: bool | None = None
