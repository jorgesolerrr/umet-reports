from mysql.connector import connect
from .settings import settings
from src.logging.logger_factory import get_logger

logger = get_logger()

def get_connection():
    try:
        conn = connect(
            user=settings.DB_DATOSOL_USER,
            password=settings.DB_DATOSOL_PASSWORD,
            host=settings.DB_DATOSOL_SERVER,
            port=settings.DB_DATOSOL_PORT,
            database=settings.DB_DATOSOL_NAME
        )
        logger.info("Conexión a la base de datos establecida")
        return conn
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise e
    