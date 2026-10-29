from typing import Optional

from pydantic import BaseModel, Field


class ColmeiaCreate(BaseModel):
    codigo: str = Field(..., min_length=1)
    nome: str = Field(..., min_length=1)
    localizacao: str = Field(..., min_length=1)
    status: str = Field(default="ativa")
    observacoes: Optional[str] = None


class ColmeiaResponse(BaseModel):
    id_colmeia: Optional[str] = None
    codigo: str
    nome: str
    localizacao: str
    status: str
    observacoes: Optional[str] = None
