from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Configuración de Moodle
    MOODLE_URL: str
    MOODLE_TOKEN: str
    MOODLE_NAME: str = "grades"
    
    # Patrones de búsqueda de cursos
    COURSE_PATTERNS: List[str] = ["GRA-PA66", "UAFTT-PA12"]
    
    # Posición del OFG en el shortname (split por "-")
    OFG_POS: int = -3
    
    # Base de datos Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Configuración de logging
    LOG_TO_CONSOLE: bool = True
    LOG_TO_FILE: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/grades.log"
    INTERCEPT_MODULES: List[str] = ["redis", "httpx"]

    
    class Config:
        env_file = ".env.grades"  # Archivo .env personalizado
        env_file_encoding = "utf-8"
        


settings = Settings()
