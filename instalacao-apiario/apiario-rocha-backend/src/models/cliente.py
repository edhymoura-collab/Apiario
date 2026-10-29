from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    email: str | None = Field(default=None, min_length=1)
    telefone: str | None = Field(default=None, min_length=1)
    documento: str | None = Field(default=None, min_length=1)
    cidade: str | None = Field(default=None, min_length=1)
    tipo: str = Field(default="pf", min_length=1)
    observacoes: str | None = Field(default=None, min_length=1)


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    telefone: str | None = Field(default=None, min_length=1)
    documento: str | None = Field(default=None, min_length=1)
    cidade: str | None = Field(default=None, min_length=1)
    tipo: str | None = Field(default=None, min_length=1)
    observacoes: str | None = Field(default=None, min_length=1)
