import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Fleet Maintenance System")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "troque_essa_chave_em_producao")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://127.0.0.1:5500,http://localhost:5500,https://frontend-equipamentos-six.vercel.app"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()