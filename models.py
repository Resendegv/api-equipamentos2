from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)

    equipamentos = relationship("Equipamento", back_populates="usuario", cascade="all, delete")
    manutencoes = relationship("Manutencao", back_populates="usuario", cascade="all, delete")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    fabricante = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    status = Column(String, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="equipamentos")
    manutencoes = relationship("Manutencao", back_populates="equipamento", cascade="all, delete")


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String, nullable=False)
    status = Column(String, nullable=False)

    # 🔥 JÁ EXISTENTE
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # 🔥 NOVOS CAMPOS (PRAZO)
    data_prevista = Column(DateTime, nullable=True)
    data_conclusao = Column(DateTime, nullable=True)

    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    equipamento = relationship("Equipamento", back_populates="manutencoes")
    usuario = relationship("Usuario", back_populates="manutencoes")