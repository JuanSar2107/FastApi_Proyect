from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Gestión de Inventarios"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./inventario.db"
    SECRET_KEY: str = "cambia-esta-clave-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    # CORS settings - can be overridden via environment variable CORS_ORIGINS
    CORS_ORIGINS: List[str] = ["https://www.flutter.proyecto.lol", "http://localhost:3000", "http://localhost:8080"]


settings = Settings()
