from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Base de datos DATOSOL
    DB_DATOSOL_USER: str
    DB_DATOSOL_PASSWORD: str
    DB_DATOSOL_SERVER: str
    DB_DATOSOL_PORT: str
    DB_DATOSOL_NAME: str
    
    
    # Base de datos Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Configuración de logging
    LOG_TO_CONSOLE: bool = True
    LOG_TO_FILE: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/educontrol.log"
    INTERCEPT_MODULES: List[str] = ["redis", "httpx"]


    class Config:
        env_file = ".env.educontrol"  # Archivo .env personalizado
        env_file_encoding = "utf-8"
        


settings = Settings()
