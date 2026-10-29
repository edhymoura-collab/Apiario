from pydantic import BaseModel, Field


class FornecedorCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    cnpj: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    telefone: str | None = Field(default=None, min_length=1)
    categoria: str | None = Field(default=None, min_length=1)
    cidade: str | None = Field(default=None, min_length=1)
    observacoes: str | None = Field(default=None, min_length=1)


class FornecedorUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    cnpj: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    telefone: str | None = Field(default=None, min_length=1)
    categoria: str | None = Field(default=None, min_length=1)
    cidade: str | None = Field(default=None, min_length=1)
    observacoes: str | None = Field(default=None, min_length=1)
