from pydantic import BaseModel, ConfigDict, Field


class EmpresaProfile(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    razaoSocial: str | None = Field(default=None)
    nomeFantasia: str | None = Field(default=None)
    cnpj: str | None = Field(default=None)
    inscricaoEstadual: str | None = Field(default=None)
    endereco: str | None = Field(default=None)
    numero: str | None = Field(default=None)
    complemento: str | None = Field(default=None)
    bairro: str | None = Field(default=None)
    cidade: str | None = Field(default=None)
    estado: str | None = Field(default=None)
    cep: str | None = Field(default=None)
    telefone: str | None = Field(default=None)
    email: str | None = Field(default=None)
    site: str | None = Field(default=None)
    segmento: str | None = Field(default=None)
    logoUrl: str | None = Field(default=None)
