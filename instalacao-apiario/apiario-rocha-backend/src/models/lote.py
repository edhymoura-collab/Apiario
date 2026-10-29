from typing import Optional

from pydantic import BaseModel, Field


class LotePublico(BaseModel):
    codigo_lote: str
    variedade_florada: str
    data_extracao: str
    umidade: float
    pureza: float
    quantidade_potes: int
    laboratorio: str
    storytelling: str


class LoteCreate(BaseModel):
    codigo_lote: str = Field(..., min_length=1)
    variedade_florada: str = Field(..., min_length=1)
    data_extracao: str = Field(..., min_length=1)
    umidade: float = Field(..., ge=0)
    pureza: float = Field(..., ge=0)
    quantidade_potes: int = Field(..., gt=0)
    laboratorio: str = Field(..., min_length=1)
    storytelling: str = Field(..., min_length=1)
    auditado: bool = True
    id_colmeia: Optional[str] = None
