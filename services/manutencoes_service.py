from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Equipamento, Manutencao


STATUS_EM_ANDAMENTO = {"em andamento"}
STATUS_CONCLUIDOS = {"concluida", "concluída", "finalizada", "encerrada"}


def normalizar_texto(texto: str | None) -> str:
    return (texto or "").strip().lower()


def status_em_andamento(status: str | None) -> bool:
    return normalizar_texto(status) in STATUS_EM_ANDAMENTO


def status_concluida(status: str | None) -> bool:
    return normalizar_texto(status) in STATUS_CONCLUIDOS


def buscar_manutencao_do_usuario(db: Session, manutencao_id: int, usuario_id: int) -> Manutencao | None:
    return (
        db.query(Manutencao)
        .filter(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == usuario_id
        )
        .first()
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


def calcular_status_prazo(manutencao: Manutencao):
    if not manutencao.data_prevista:
        return None, None, None

    agora = datetime.utcnow()

    if status_concluida(manutencao.status):
        if manutencao.data_conclusao:
            diferenca = (manutencao.data_conclusao - manutencao.data_prevista).days
            if diferenca <= 0:
                return 0, None, "concluída no prazo"
            return None, diferenca, "concluída atrasada"
        return None, None, "concluída"

    dias_restantes = (manutencao.data_prevista - agora).days

    if dias_restantes >= 0:
        return dias_restantes, None, "no prazo"

    return None, abs(dias_restantes), "vencida"


def montar_item_manutencao(manutencao: Manutencao, equipamento_nome: str | None = None):
    prazo_restante, vencida_dias, status_prazo = calcular_status_prazo(manutencao)

    return {
        "id": manutencao.id,
        "titulo": manutencao.titulo,
        "descricao": manutencao.descricao,
        "prioridade": manutencao.prioridade,
        "status": manutencao.status,
        "data_criacao": manutencao.data_criacao,
        "data_prevista": manutencao.data_prevista,
        "data_conclusao": manutencao.data_conclusao,
        "equipamento_id": manutencao.equipamento_id,
        "usuario_id": manutencao.usuario_id,
        "equipamento_nome": equipamento_nome,
        "prazo_restante": prazo_restante,
        "vencida_dias": vencida_dias,
        "status_prazo": status_prazo,
    }


def atualizar_status_equipamento(db: Session, equipamento_id: int, usuario_id: int):
    equipamento = buscar_equipamento_do_usuario(db, equipamento_id, usuario_id)
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

    existe_em_andamento = any(status_em_andamento(item.status) for item in manutencoes)

    if existe_em_andamento:
        equipamento.status = "em manutenção"
    elif equipamento.status == "em manutenção":
        equipamento.status = "operando"


def listar_manutencoes_do_usuario(db: Session, usuario_id: int, pagina: int, por_pagina: int):
    query = db.query(Manutencao).filter(Manutencao.usuario_id == usuario_id)

    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina if total > 0 else 1

    manutencoes = (
        query.order_by(Manutencao.id.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    dados = []
    for manutencao in manutencoes:
        equipamento = buscar_equipamento_do_usuario(db, manutencao.equipamento_id, usuario_id)
        dados.append(
            montar_item_manutencao(
                manutencao,
                equipamento.nome if equipamento else "Desconhecido"
            )
        )

    return {
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_paginas": total_paginas,
        "dados": dados
    }


def listar_manutencoes_por_equipamento(db: Session, equipamento: Equipamento, usuario_id: int):
    manutencoes = (
        db.query(Manutencao)
        .filter(
            Manutencao.equipamento_id == equipamento.id,
            Manutencao.usuario_id == usuario_id
        )
        .order_by(Manutencao.id.desc())
        .all()
    )

    return [
        montar_item_manutencao(item, equipamento.nome)
        for item in manutencoes
    ]


def criar_manutencao(db: Session, usuario_id: int, dados):
    equipamento = buscar_equipamento_do_usuario(db, dados.equipamento_id, usuario_id)
    if not equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    nova = Manutencao(
        titulo=dados.titulo,
        descricao=dados.descricao,
        prioridade=dados.prioridade,
        status=dados.status,
        equipamento_id=dados.equipamento_id,
        usuario_id=usuario_id,
        data_prevista=dados.data_prevista,
        data_conclusao=dados.data_conclusao
    )

    db.add(nova)
    db.flush()

    atualizar_status_equipamento(db, dados.equipamento_id, usuario_id)

    db.commit()
    db.refresh(nova)
    db.refresh(equipamento)

    return {
        "message": "Manutenção criada com sucesso",
        "manutencao": montar_item_manutencao(nova, equipamento.nome)
    }


def atualizar_manutencao(db: Session, manutencao: Manutencao, usuario_id: int, dados):
    equipamento_id_anterior = manutencao.equipamento_id

    if dados.equipamento_id is not None:
        equipamento_destino = buscar_equipamento_do_usuario(db, dados.equipamento_id, usuario_id)
        if not equipamento_destino:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        manutencao.equipamento_id = dados.equipamento_id

    if dados.titulo is not None:
        manutencao.titulo = dados.titulo

    if dados.descricao is not None:
        manutencao.descricao = dados.descricao

    if dados.prioridade is not None:
        manutencao.prioridade = dados.prioridade

    if dados.status is not None:
        manutencao.status = dados.status
        if status_concluida(dados.status) and manutencao.data_conclusao is None:
            manutencao.data_conclusao = datetime.utcnow()

    if dados.data_prevista is not None:
        manutencao.data_prevista = dados.data_prevista

    if dados.data_conclusao is not None:
        manutencao.data_conclusao = dados.data_conclusao

    db.flush()

    atualizar_status_equipamento(db, equipamento_id_anterior, usuario_id)
    atualizar_status_equipamento(db, manutencao.equipamento_id, usuario_id)

    db.commit()
    db.refresh(manutencao)

    equipamento = buscar_equipamento_do_usuario(db, manutencao.equipamento_id, usuario_id)

    return {
        "message": "Manutenção atualizada com sucesso",
        "manutencao": montar_item_manutencao(
            manutencao,
            equipamento.nome if equipamento else "Desconhecido"
        )
    }


def deletar_manutencao(db: Session, manutencao: Manutencao, usuario_id: int):
    equipamento_id = manutencao.equipamento_id

    db.delete(manutencao)
    db.flush()

    atualizar_status_equipamento(db, equipamento_id, usuario_id)

    db.commit()

    return {"message": "Manutenção deletada com sucesso"}