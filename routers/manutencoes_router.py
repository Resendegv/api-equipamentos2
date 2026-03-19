from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from models import Manutencao, Equipamento, Usuario
from schemas import ManutencaoCreate, ManutencaoUpdate
from auth import get_current_user

router = APIRouter(prefix="/manutencoes", tags=["Manutenções"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def status_em_aberto(status: str) -> bool:
    return (status or "").strip().lower() in ["aberta", "em andamento", "pendente"]


def status_concluida(status: str) -> bool:
    return (status or "").strip().lower() in ["concluida", "concluída", "finalizada", "encerrada"]


def calcular_status_prazo(manutencao):
    data_prevista = getattr(manutencao, "data_prevista", None)
    data_conclusao = getattr(manutencao, "data_conclusao", None)

    if not data_prevista:
        return None, None, None

    agora = datetime.utcnow()

    if status_concluida(manutencao.status):
        if data_conclusao:
            diferenca = (data_conclusao - data_prevista).days
            if diferenca <= 0:
                return 0, None, "concluída no prazo"
            return None, diferenca, "concluída atrasada"
        return None, None, "concluída"

    dias_restantes = (data_prevista - agora).days

    if dias_restantes >= 0:
        return dias_restantes, None, "no prazo"

    return None, abs(dias_restantes), "vencida"


def montar_item_manutencao(manutencao, equipamento_nome="Desconhecido"):
    prazo_restante, vencida_dias, status_prazo = calcular_status_prazo(manutencao)

    item = {
        "id": manutencao.id,
        "titulo": manutencao.titulo,
        "descricao": manutencao.descricao,
        "tipo": manutencao.tipo,
        "status": manutencao.status,
        "equipamento_id": manutencao.equipamento_id,
        "equipamento_nome": equipamento_nome,
        "prazo_restante": prazo_restante,
        "vencida_dias": vencida_dias,
        "status_prazo": status_prazo,
    }

    if hasattr(manutencao, "data_criacao"):
        item["data_criacao"] = manutencao.data_criacao

    if hasattr(manutencao, "data_prevista"):
        item["data_prevista"] = manutencao.data_prevista

    if hasattr(manutencao, "data_conclusao"):
        item["data_conclusao"] = manutencao.data_conclusao

    return item


def atualizar_status_equipamento(db: Session, equipamento_id: int, usuario_id: int):
    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == equipamento_id,
            Equipamento.usuario_id == usuario_id
        )
        .first()
    )

    if not equipamento:
        return

    manutencoes = (
        db.query(Manutencao)
        .filter(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.usuario_id == usuario_id
        )
        .all()
    )

    existe_aberta = any(status_em_aberto(m.status) for m in manutencoes)

    if existe_aberta:
        equipamento.status = "em manutenção"
    elif equipamento.status == "em manutenção":
        equipamento.status = "operando"


@router.get("/")
def listar_manutencoes(
    pagina: int = 1,
    por_pagina: int = 100,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencoes = (
        db.query(Manutencao)
        .filter(Manutencao.usuario_id == usuario.id)
        .order_by(Manutencao.id.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    resultado = []

    for manutencao in manutencoes:
        equipamento = (
            db.query(Equipamento)
            .filter(
                Equipamento.id == manutencao.equipamento_id,
                Equipamento.usuario_id == usuario.id
            )
            .first()
        )

        resultado.append(
            montar_item_manutencao(
                manutencao,
                equipamento.nome if equipamento else "Desconhecido"
            )
        )

    return {"dados": resultado}


@router.get("/equipamento/{equipamento_id}")
def listar_manutencoes_por_equipamento(
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

    manutencoes = (
        db.query(Manutencao)
        .filter(
            Manutencao.equipamento_id == equipamento_id,
            Manutencao.usuario_id == usuario.id
        )
        .order_by(Manutencao.id.desc())
        .all()
    )

    resultado = [
        montar_item_manutencao(manutencao, equipamento.nome)
        for manutencao in manutencoes
    ]

    return {
        "equipamento": {
            "id": equipamento.id,
            "nome": equipamento.nome,
            "modelo": equipamento.modelo,
            "fabricante": equipamento.fabricante,
            "ano": equipamento.ano,
            "status": equipamento.status
        },
        "manutencoes": resultado
    }


@router.get("/{manutencao_id}")
def buscar_manutencao(
    manutencao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = (
        db.query(Manutencao)
        .filter(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == usuario.id
        )
        .first()
    )

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == manutencao.equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    return montar_item_manutencao(
        manutencao,
        equipamento.nome if equipamento else "Desconhecido"
    )


@router.post("/")
def criar_manutencao(
    dados: ManutencaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == dados.equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    nova_manutencao = Manutencao(
        titulo=dados.titulo,
        descricao=dados.descricao,
        tipo=dados.tipo,
        status=dados.status,
        equipamento_id=dados.equipamento_id,
        usuario_id=usuario.id,
        data_prevista=dados.data_prevista
    )

    db.add(nova_manutencao)

    if status_em_aberto(dados.status):
        equipamento.status = "em manutenção"

    db.commit()
    db.refresh(nova_manutencao)

    return {
        "mensagem": "Manutenção criada com sucesso",
        "manutencao": montar_item_manutencao(nova_manutencao, equipamento.nome)
    }


@router.put("/{manutencao_id}")
def atualizar_manutencao(
    manutencao_id: int,
    dados: ManutencaoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = (
        db.query(Manutencao)
        .filter(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == usuario.id
        )
        .first()
    )

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    equipamento_id_anterior = manutencao.equipamento_id

    if dados.equipamento_id is not None:
        equipamento_destino = (
            db.query(Equipamento)
            .filter(
                Equipamento.id == dados.equipamento_id,
                Equipamento.usuario_id == usuario.id
            )
            .first()
        )

        if not equipamento_destino:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        manutencao.equipamento_id = dados.equipamento_id

    if dados.titulo is not None:
        manutencao.titulo = dados.titulo

    if dados.descricao is not None:
        manutencao.descricao = dados.descricao

    if dados.tipo is not None:
        manutencao.tipo = dados.tipo

    if dados.status is not None:
        manutencao.status = dados.status

        if status_concluida(dados.status):
            if hasattr(manutencao, "data_conclusao") and manutencao.data_conclusao is None:
                manutencao.data_conclusao = datetime.utcnow()

    if hasattr(dados, "data_prevista") and dados.data_prevista is not None:
        manutencao.data_prevista = dados.data_prevista

    if hasattr(dados, "data_conclusao") and dados.data_conclusao is not None:
        manutencao.data_conclusao = dados.data_conclusao

    db.commit()

    atualizar_status_equipamento(db, equipamento_id_anterior, usuario.id)
    atualizar_status_equipamento(db, manutencao.equipamento_id, usuario.id)

    db.commit()
    db.refresh(manutencao)

    equipamento = (
        db.query(Equipamento)
        .filter(
            Equipamento.id == manutencao.equipamento_id,
            Equipamento.usuario_id == usuario.id
        )
        .first()
    )

    return {
        "mensagem": "Manutenção atualizada com sucesso",
        "manutencao": montar_item_manutencao(
            manutencao,
            equipamento.nome if equipamento else "Desconhecido"
        )
    }


@router.delete("/{manutencao_id}")
def deletar_manutencao(
    manutencao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    manutencao = (
        db.query(Manutencao)
        .filter(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == usuario.id
        )
        .first()
    )

    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")

    equipamento_id = manutencao.equipamento_id

    db.delete(manutencao)
    db.commit()

    atualizar_status_equipamento(db, equipamento_id, usuario.id)
    db.commit()

    return {"mensagem": "Manutenção deletada com sucesso"}