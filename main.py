from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import Base, engine
from routers.auth_router import router as auth_router
from routers.equipamentos_router import router as equipamentos_router
from routers.manutencoes_router import router as manutencoes_router

app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
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