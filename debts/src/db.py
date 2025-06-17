import logging
from typing import Generator
from mysql.connector import connect, MySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.errors import DatabaseError
from .settings import settings
from .schemas import MoodleConn
from src.logging.logger_factory import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log

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
    urlStr = url.split("/")
    return "/".join(urlStr[:3])

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
                            lms.dbprograms 
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
            ) for result in result]

    except Exception as e:
        logger.error(f"Error al obtener LMS disponibles: {e}")
        raise e

def get_suspended_users(db: MySQLConnection, lmsName: str) -> set[str]:
    """Method to obtain current suspended users from tbSuspended

    Args:
        db (MySQLConnection): current connection of db session

    Returns:
        set of ("cédula"): users remains suspended on logs table
    """
    try:
        with db.cursor() as cursor:
            tempSQL = "select susp.cedula from tbSuspended AS susp where (susp.lmsname = %s)"
            cursor.execute(tempSQL, [lmsName])
            result = cursor.fetchall()
            logger.info(f"Se han obtenido {len(result)} usuarios suspendidos")
            return {muser[0] for muser in result}
    except Exception as e:
        logger.error(f"Error al obtener usuarios suspendidos: {e}")
        raise e
def post_suspended_user(db: MySQLConnection, lmsName: str, user: dict):
    
    try:
        
        with db.cursor() as cursor:
            tempSQL = "insert into tbSuspended (programa, cedula, descrip, lmsname) values(%s, %s, %s, %s)"
            cursor.execute(tempSQL, (user["programa"], user["cedula"], user["descrip"], lmsName))
            db.commit()
            logger.info(f"Se suspendió el usuario {user['cedula']}")
            
    except DatabaseError as e:
        logger.error(f"Error al insertar usuarios suspendidos: {e}")
        db.rollback()
        raise e
    except Exception as e:
        logger.error(f"Error al insertar usuarios suspendidos: {e}")
        raise e

def delete_suspended_user(db: MySQLConnection, lmsName: str, user: dict):
    try:
        with db.cursor() as cursor:
            tempSQL = "delete from tbSuspended where (cedula = %s) and (lmsname = %s)"
            cursor.execute(tempSQL, (user["cedula"], lmsName))
            db.commit()
            logger.info(f"Se ha activado el usuario {user['cedula']}")
    except Exception as e:
        logger.error(f"Error al eliminar usuarios suspendidos: {e}")
        raise e