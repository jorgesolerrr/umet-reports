from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
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
    SMTP_TLS: bool = True
    TEMPLATES_PATH: str = "debts/templates"
    APP_FERMET_KEY: str
    ENCODING_STRING: str
    APP_SECRET: str
    REPORT_NOTIFICATION: str
    MINUTES_TO_RUN: int = 60
    

        

settings = Settings()