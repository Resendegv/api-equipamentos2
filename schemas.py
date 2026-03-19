from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    username: str
    password: str


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


class EquipamentoCreate(BaseModel):
    nome: str
    modelo: str
    fabricante: str
    ano: int
    status: str


class EquipamentoUpdate(BaseModel):
    nome: str
    modelo: str
    fabricante: str
    ano: int
    status: str


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


# 🔥 NOVO
class ManutencaoCreate(BaseModel):
    titulo: str
    descricao: str
    tipo: str
    status: str
    equipamento_id: int
    data_prevista: Optional[datetime] = None


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
    descricao: str
    tipo: str
    status: str
    data_criacao: datetime
    data_prevista: Optional[datetime]
    data_conclusao: Optional[datetime]
    equipamento_id: int
    usuario_id: int

    # 🔥 CAMPOS CALCULADOS
    prazo_restante: Optional[int]
    vencida_dias: Optional[int]
    status_prazo: Optional[str]

    class Config:
        from_attributes = True


class EstatisticasOut(BaseModel):
    total_equipamentos: int
    total_manutencoes: int
    equipamentos_operacionais: int
    equipamentos_em_manutencao: int
    equipamentos_parados: int
    manutencoes_abertas: int
    manutencoes_concluidas: int


class DashboardOut(BaseModel):
    equipamentos: dict
    manutencoes: dict