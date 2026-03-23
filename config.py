import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Fleet Maintenance System")
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

    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL", "").strip()

        if not url:
            raise ValueError(
                "DATABASE_URL não foi definida. Configure essa variável no ambiente do Render."
            )

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

        return url


settings = Settings()