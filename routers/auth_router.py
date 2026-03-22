from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from models import Usuario
from schemas import MessageResponse, Token, UsuarioCreate, UsuarioLogin, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.username == data.username).first()

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
    usuario = db.query(Usuario).filter(Usuario.username == data.username).first()

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
    usuario = db.query(Usuario).filter(Usuario.username == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário inválido")

    if not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Senha inválida")

    token = create_access_token({"sub": usuario.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario