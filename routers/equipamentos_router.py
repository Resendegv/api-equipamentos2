from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Usuario
from schemas import (
    EquipamentoCreate,
    EquipamentoListResponse,
    EquipamentoOut,
    EquipamentoUpdate,
    MessageResponse,
)
from services.equipamentos_service import (
    atualizar_equipamento,
    buscar_equipamento_do_usuario,
    criar_equipamento,
    deletar_equipamento,
    listar_equipamentos_do_usuario,
)

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])


@router.post("/", response_model=EquipamentoOut, status_code=status.HTTP_201_CREATED)
def criar(
    dados: EquipamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    try:
        return criar_equipamento(db, usuario.id, dados)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar equipamento: {str(e)}"
        )


@router.get("/", response_model=EquipamentoListResponse)
def listar(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    return listar_equipamentos_do_usuario(db, usuario.id, pagina, por_pagina)


@router.get("/{equipamento_id}", response_model=EquipamentoOut)
def buscar(
    equipamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = buscar_equipamento_do_usuario(db, equipamento_id, usuario.id)

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    return equipamento


@router.put("/{equipamento_id}", response_model=EquipamentoOut)
def atualizar(
    equipamento_id: int,
    dados: EquipamentoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = buscar_equipamento_do_usuario(db, equipamento_id, usuario.id)

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    try:
        return atualizar_equipamento(db, equipamento, usuario.id, dados)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao atualizar equipamento: {str(e)}"
        )


@router.delete("/{equipamento_id}", response_model=MessageResponse)
def deletar(
    equipamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = buscar_equipamento_do_usuario(db, equipamento_id, usuario.id)

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    try:
        deletar_equipamento(db, equipamento)
        return {"message": "Equipamento deletado com sucesso"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir este equipamento porque existem manutenções vinculadas a ele."
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao excluir equipamento: {str(e)}"
        )