from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Gestión de Inventarios"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./inventario.db"
    SECRET_KEY: str = "cambia-esta-clave-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    # Orígenes CORS permitidos, separados por comas (variable de entorno CORS_ORIGINS).
    # No usar "*": allow_credentials=True lo hace inválido.
    CORS_ORIGINS: str = (
        "https://flutter.proyecto.lol,"
        "https://www.flutter.proyecto.lol,"
        "http://localhost:8044,"
        "http://127.0.0.1:8044"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip().rstrip("/") for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
