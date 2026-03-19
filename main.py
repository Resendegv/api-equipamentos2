from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

# IMPORTS CORRETOS
from routers.auth_router import router as auth_router
from routers.equipamentos_router import router as equipamentos_router
from routers.manutencoes_router import router as manutencoes_router

# CRIA AS TABELAS
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fleet Maintenance System")

# CORS (liberar frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://SEU-FRONTEND.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROTAS
app.include_router(auth_router)
app.include_router(equipamentos_router)
app.include_router(manutencoes_router)

# ROTA TESTE
@app.get("/")
def home():
    return {"message": "Fleet Maintenance API online 🚀"}