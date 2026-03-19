from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers.auth_router import router as auth_router
from routers.equipamentos_router import router as equipamentos_router
from routers.manutencoes_router import router as manutencoes_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fleet Maintenance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://frontend-equipamentos-six.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(equipamentos_router)
app.include_router(manutencoes_router)


@app.get("/")
def home():
    return {"message": "Fleet Maintenance API online 🚀"}