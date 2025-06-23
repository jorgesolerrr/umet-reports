from tenacity import stop_after_attempt, wait_fixed, before_log, after_log, retry
from src.schemas import MoodleConn
from src.settings import settings
from src.utils.logging.logger_factory import get_logger
import logging
from typing import Generator
from mysql.connector import MySQLConnection, connect

logger = get_logger()

MAX_ATTEMPTS = 3
WAIT_TIME = 1


@retry(
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_fixed(WAIT_TIME),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
def get_db() -> Generator[MySQLConnection, None, None]:
    try:
        conn = connect(
            user=settings.DB_DATOSOL_USER,
            password=settings.DB_DATOSOL_PASSWORD,
            host=settings.DB_DATOSOL_SERVER,
            port=settings.DB_DATOSOL_PORT,
            database=settings.DB_DATOSOL_NAME,
        )
        logger.info("Conexión a la base de datos DATOSOL establecida")
        yield conn
        conn.close()
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise e
    
def parse_url(url: str) -> str:
    return url.split("/")[2]

def get_available_lms(gwDBCursor: MySQLConnection) -> list[MoodleConn]:
    # sourcery skip: extract-method
    try:
        with gwDBCursor.cursor() as cursor:
            tempSQL = """
                        select 
                            lms.id,
                            lms.url_moodle_service, 
                            lms.dbname, 
                            lms.dbuser, 
                            lms.dbpass, 
                            lms.dbprograms,
                            lms.lmsName
                        from tbLMS AS lms 
                        where (lms.enabled = 1)"""
            logger.info("Ejecutando consulta para obtener LMS disponibles")
            cursor.execute(tempSQL)
            result = cursor.fetchall()
            logger.info(f"Se han obtenido {len(result)} LMS disponibles")
            
            return [MoodleConn(
                host=parse_url(result[1]),
                port=3306,
                db_name=result[2],
                db_user=result[3],
                db_password=result[4],
                db_programs=result[5],
                lms_name=result[6]
            ) for result in result]

    except Exception as e:
        logger.error(f"Error al obtener LMS disponibles: {e}")
        raise e