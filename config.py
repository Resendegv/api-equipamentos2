import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Fleet Maintenance System")

    # Para produção, o ideal é SEMPRE usar DATABASE_URL do ambiente.
    # Mantive um fallback local para facilitar testes, mas agora já em PostgreSQL.
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/fleet_maintenance"
    )

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
    def database_url_normalized(self) -> str:
        """
        Normaliza a URL para o formato esperado pelo SQLAlchemy.
        Render/alguns provedores podem fornecer postgres://
        e o SQLAlchemy prefere postgresql+psycopg2://
        """
        url = self.DATABASE_URL.strip()

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

        return url


settings = Settings()