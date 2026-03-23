from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Equipamento, Manutencao


STATUS_ABERTOS = {"aberta", "em andamento", "pendente"}
STATUS_EQUIPAMENTO_VALIDOS = {"operando", "parado"}


def normalizar_texto(texto: str | None) -> str:
    return (texto or "").strip().lower()


def status_em_aberto(status: str | None) -> bool:
    return normalizar_texto(status) in STATUS_ABERTOS


def validar_status_manual(status: str) -> str:
    status_normalizado = normalizar_texto(status)

    if status_normalizado in {"operando", "operacional"}:
        return "operando"

    if status_normalizado == "parado":
        return "parado"

    if status_normalizado in {"em manutenção", "em manutencao", "manutenção", "manutencao"}:
        raise HTTPException(
            status_code=400,
            detail='O status "em manutenção" é definido automaticamente pelo sistema'
        )

    raise HTTPException(
        status_code=400,
        detail='Status inválido. Use apenas "operando" ou "parado"'
    )


def buscar_equipamento_do_usuario(db: Session, equipamento_id: int, usuario_id: int) -> Equipamento | None:
    return (
        db.query(Equipamento)
        .filter(
            Equipamento.id == equipamento_id,
            Equipamento.usuario_id == usuario_id
        )
        .first()
    )


def listar_equipamentos_do_usuario(db: Session, usuario_id: int, pagina: int, por_pagina: int):
    query = db.query(Equipamento).filter(Equipamento.usuario_id == usuario_id)

    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina if total > 0 else 1

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


def existe_manutencao(db: Session, equipamento_id: int, usuario_id: int) -> bool:
    return (
        db.query(Manutencao)
        .filter(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.usuario_id == usuario_id
        )
        .first()
        is not None
    )


def criar_equipamento(db: Session, usuario_id: int, dados):
    status_final = validar_status_manual(dados.status)

    equipamento = Equipamento(
        nome=dados.nome,
        modelo=dados.modelo,
        fabricante=dados.fabricante,
        ano=dados.ano,
        status=status_final,
        usuario_id=usuario_id
    )

    db.add(equipamento)
    db.commit()
    db.refresh(equipamento)
    return equipamento


def atualizar_equipamento(db: Session, equipamento: Equipamento, usuario_id: int, dados):
    equipamento.nome = dados.nome
    equipamento.modelo = dados.modelo
    equipamento.fabricante = dados.fabricante
    equipamento.ano = dados.ano

    if existe_manutencao(db, equipamento.id, usuario_id):
        equipamento.status = "em manutenção"
    else:
        equipamento.status = validar_status_manual(dados.status)

    db.commit()
    db.refresh(equipamento)
    return equipamento


def deletar_equipamento(db: Session, equipamento: Equipamento, usuario_id: int):
    
    # 🔥 VALIDAÇÃO CRÍTICA
    if existe_manutencao(db, equipamento.id, usuario_id):
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir: existem manutenções vinculadas a este equipamento"
        )

    try:
        db.delete(equipamento)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar equipamento: {str(e)}"
        )