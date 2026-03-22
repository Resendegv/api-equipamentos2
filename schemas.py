from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=100)


class UsuarioLogin(BaseModel):
    username: str
    password: str


class UsuarioOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class EquipamentoBase(BaseModel):
    nome: str
    modelo: str
    fabricante: str
    ano: int
    status: str


class EquipamentoCreate(EquipamentoBase):
    pass


class EquipamentoUpdate(EquipamentoBase):
    pass


class EquipamentoOut(BaseModel):
    id: int
    nome: str
    modelo: str
    fabricante: str
    ano: int
    status: str
    usuario_id: int

    class Config:
        from_attributes = True


class EquipamentoListResponse(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int
    dados: list[EquipamentoOut]


class ManutencaoBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tipo: str
    status: str
    data_prevista: Optional[datetime] = None


class ManutencaoCreate(ManutencaoBase):
    equipamento_id: int


class ManutencaoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    equipamento_id: Optional[int] = None
    data_prevista: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None


class ManutencaoOut(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    tipo: str
    status: str
    data_criacao: datetime
    data_prevista: Optional[datetime]
    data_conclusao: Optional[datetime]
    equipamento_id: int
    usuario_id: int
    equipamento_nome: Optional[str] = None
    prazo_restante: Optional[int] = None
    vencida_dias: Optional[int] = None
    status_prazo: Optional[str] = None

    class Config:
        from_attributes = True


class ManutencaoListResponse(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int
    dados: list[ManutencaoOut]


class EquipamentoComManutencoesResponse(BaseModel):
    equipamento: EquipamentoOut
    manutencoes: list[ManutencaoOut]