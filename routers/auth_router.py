from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioLogin, Token
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.username == data.username)
        .first()
    )

    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo = Usuario(
        username=data.username,
        senha_hash=hash_password(data.password)
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {"message": "Usuário criado com sucesso"}


@router.post("/login", response_model=Token)
def login_json(data: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.username == data.username)
        .first()
    )

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário inválido")

    if not verify_password(data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Senha inválida")

    token = create_access_token({"sub": usuario.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_form_compat(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = (
        db.query(Usuario)
        .filter(Usuario.username == form_data.username)
        .first()
    )

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário inválido")

    if not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Senha inválida")

    token = create_access_token({"sub": usuario.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }