from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_DATOSOL_USER: str
    DB_DATOSOL_PASSWORD: str
    DB_DATOSOL_SERVER: str
    DB_DATOSOL_PORT: str
    DB_DATOSOL_NAME: str
    LOG_TO_CONSOLE: bool = True
    LOG_TO_FILE: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    INTERCEPT_MODULES: list[str] = ["mysql.connector"]
    SUSPENDED_NOTIFICATION: str
    ACTIVATED_NOTIFICATION: str
    DEBT_NOTIFICATION: str
    SMTP_SERVER: str
    SMTP_PORT: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    class Config:
        env_file = ".env"

settings = Settings()