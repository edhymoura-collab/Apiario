from typing import Optional

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    perfil: str = Field(default="usuario")


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1)
    email: Optional[str] = Field(default=None, min_length=1)
    username: Optional[str] = Field(default=None, min_length=3)
    password: Optional[str] = Field(default=None, min_length=6)
    perfil: Optional[str] = None


class AdministradorCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    nivel: str = Field(default="admin")


class AdministradorUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1)
    email: Optional[str] = Field(default=None, min_length=1)
    username: Optional[str] = Field(default=None, min_length=3)
    password: Optional[str] = Field(default=None, min_length=6)
    nivel: Optional[str] = None


class FuncionarioCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    cargo: str = Field(..., min_length=1)
    departamento: str = Field(..., min_length=1)
    salario: float = Field(..., gt=0)
    status: str = Field(default="ativo")
    observacoes: Optional[str] = None


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1)
    email: Optional[str] = Field(default=None, min_length=1)
    cargo: Optional[str] = Field(default=None, min_length=1)
    departamento: Optional[str] = Field(default=None, min_length=1)
    salario: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None
    observacoes: Optional[str] = None
