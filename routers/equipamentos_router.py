from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Equipamento, Usuario, Manutencao
from schemas import EquipamentoCreate, EquipamentoUpdate
from auth import get_current_user

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])


def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    return texto.strip().lower()


def existe_manutencao_aberta(db: Session, equipamento_id: int, usuario_id: int) -> bool:
    manutencoes = (
        db.query(Manutencao)
        .filter(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.usuario_id == usuario_id
        )
        .all()
    )

    return any(
        normalizar_texto(m.status) in ["aberta", "em andamento", "pendente"]
        for m in manutencoes
    )


def validar_status_manual(status: str) -> str:
    status_normalizado = normalizar_texto(status)

    if status_normalizado in ["operando", "operacional"]:
        return "operando"

    if status_normalizado == "parado":
        return "parado"

    if status_normalizado in ["em manutenção", "em manutencao", "manutenção", "manutencao"]:
        raise HTTPException(
            status_code=400,
            detail='O status "em manutenção" é definido automaticamente pelo sistema'
        )

    raise HTTPException(
        status_code=400,
        detail='Status inválido. Use apenas "operando" ou "parado"'
    )


@router.post("/", status_code=201)
def criar_equipamento(
    dados: EquipamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    status_final = validar_status_manual(dados.status)

    equipamento = Equipamento(
        nome=dados.nome,
        modelo=dados.modelo,
        fabricante=dados.fabricante,
        ano=dados.ano,
        status=status_final,
        usuario_id=usuario.id
    )

    db.add(equipamento)
    db.commit()
    db.refresh(equipamento)

    return equipamento


@router.get("/")
def listar_equipamentos(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    query = db.query(Equipamento).filter(Equipamento.usuario_id == usuario.id)

    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina

    dados = (
        query.order_by(Equipamento.id.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    return {
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_paginas": total_paginas,
        "dados": dados
    }


@router.get("/{equipamento_id}")
def buscar_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    return equipamento


@router.put("/{equipamento_id}")
def atualizar_equipamento(
    equipamento_id: int,
    dados: EquipamentoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    equipamento.nome = dados.nome
    equipamento.modelo = dados.modelo
    equipamento.fabricante = dados.fabricante
    equipamento.ano = dados.ano

    if existe_manutencao_aberta(db, equipamento.id, usuario.id):
        equipamento.status = "em manutenção"
    else:
        equipamento.status = validar_status_manual(dados.status)

    db.commit()
    db.refresh(equipamento)

    return equipamento


@router.delete("/{equipamento_id}")
def deletar_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    db.delete(equipamento)
    db.commit()

    return {"message": "Equipamento deletado com sucesso"}