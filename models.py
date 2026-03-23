from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)

    equipamentos = relationship(
        "Equipamento",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    manutencoes = relationship(
        "Manutencao",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    fabricante = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="operando")

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="equipamentos")
    manutencoes = relationship(
        "Manutencao",
        back_populates="equipamento",
        cascade="all, delete-orphan"
    )


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    prioridade = Column(String, nullable=False, default="media")
    status = Column(String, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_prevista = Column(DateTime, nullable=True)
    data_conclusao = Column(DateTime, nullable=True)

    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    equipamento = relationship("Equipamento", back_populates="manutencoes")
    usuario = relationship("Usuario", back_populates="manutencoes")