from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Usuario
from schemas import (
    EquipamentoComManutencoesResponse,
    ManutencaoCreate,
    ManutencaoListResponse,
    ManutencaoOut,
    ManutencaoUpdate,
)
from services.manutencoes_service import (
    buscar_equipamento_do_usuario,
    buscar_manutencao_do_usuario,
    criar_manutencao,
    deletar_manutencao,
    listar_manutencoes_do_usuario,
    listar_manutencoes_por_equipamento,
    montar_item_manutencao,
    atualizar_manutencao,
)

router = APIRouter(prefix="/manutencoes", tags=["Manutenções"])


@router.get("/", response_model=ManutencaoListResponse)
def listar(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return listar_manutencoes_do_usuario(db, usuario.id, pagina, por_pagina)


@router.get("/equipamento/{equipamento_id}", response_model=EquipamentoComManutencoesResponse)
def listar_por_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = buscar_equipamento_do_usuario(db, equipamento_id, usuario.id)

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    manutencoes = listar_manutencoes_por_equipamento(db, equipamento, usuario.id)

    return {
        "equipamento": equipamento,
        "manutencoes": manutencoes
    }


@router.get("/{manutencao_id}", response_model=ManutencaoOut)
def buscar(
    manutencao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = buscar_manutencao_do_usuario(db, manutencao_id, usuario.id)

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    equipamento = buscar_equipamento_do_usuario(db, manutencao.equipamento_id, usuario.id)

    return montar_item_manutencao(
        manutencao,
        equipamento.nome if equipamento else "Desconhecido"
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def criar(
    dados: ManutencaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return criar_manutencao(db, usuario.id, dados)


@router.put("/{manutencao_id}")
def atualizar(
    manutencao_id: int,
    dados: ManutencaoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = buscar_manutencao_do_usuario(db, manutencao_id, usuario.id)

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    return atualizar_manutencao(db, manutencao, usuario.id, dados)


@router.delete("/{manutencao_id}")
def deletar(
    manutencao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = buscar_manutencao_do_usuario(db, manutencao_id, usuario.id)

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    return deletar_manutencao(db, manutencao, usuario.id)