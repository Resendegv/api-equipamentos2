from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers.auth_router import router as auth_router
from routers.equipamentos_router import router as equipamentos_router
from routers.manutencoes_router import router as manutencoes_router

app = FastAPI(
    title="Fleet Maintenance System",
    version="0.1.0"
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://frontend-equipamentos-six.vercel.app",
    "https://frontend-equipamentos-six.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(equipamentos_router)
app.include_router(manutencoes_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API online"}