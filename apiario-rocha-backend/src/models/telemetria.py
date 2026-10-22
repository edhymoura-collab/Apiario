from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TelemetriaCreate(BaseModel):
    id_colmeia: str = Field(..., min_length=1)
    timestamp: datetime
    peso_kg: float = Field(..., gt=0)
    temperatura_c: float
    umidade_p: float = Field(..., ge=0, le=100)
    bateria_volt: Optional[float] = None


class TelemetriaResponse(BaseModel):
    id_leitura: str
    id_colmeia: str
    timestamp_utc: datetime
    peso_kg: float
    temperatura_c: float
    umidade_p: float
    bateria_volt: Optional[float]
    criado_em: datetime


class TelemetriaHistorico(BaseModel):
    id_colmeia: str
    historico: list[TelemetriaResponse]
