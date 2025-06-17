import logging
from typing import Generator
from mysql.connector import connect, MySQLConnection
from .schemas import MoodleConn, UserMoodle
from src.logging.logger_factory import get_logger
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log
from src.utils.security import decrypt_mssg

logger = get_logger()




MAX_ATTEMPTS = 3
WAIT_TIME = 1


@retry(
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_fixed(WAIT_TIME),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
def get_moodle_db(moodleConn: MoodleConn) -> Generator[MySQLConnection, None, None]:
    try:
        conn = connect(
            host=moodleConn.host,
            port=moodleConn.port,
            user=moodleConn.db_user,
            password=decrypt_mssg(moodleConn.db_password),
            database=moodleConn.db_name
        )
        logger.info(f"Conexión a la base de datos {moodleConn.db_name} establecida")
        yield conn
        conn.close()
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos {moodleConn.db_name}: {e}")
        raise e

def path_moodle_user(moodle_conn: MySQLConnection, cedula: str, suspended: bool):
    try:
        suspended = "1" if suspended else "0"
        with moodle_conn.cursor() as cursor:
            tempSQL = "update mdl_user set mdl_user.suspended = %s where mdl_user.username = %s"  
            cursor.execute(tempSQL, [suspended, cedula])
            moodle_conn.commit()
            logger.info(f"Se ha actualizado el usuario {cedula} en Moodle a suspended = {suspended}")
        return get_moodleDBUser(moodle_conn, cedula)
    except Exception as e:
        logger.error(f"Error al actualizar el usuario {cedula} en Moodle: {e}")
        raise e
    
def get_moodleDBUser(moodle_conn: MySQLConnection, cedula: str) -> UserMoodle:
    try:
        with moodle_conn.cursor() as cursor:
            tempSQL = "select mu.id, mu.firstname, mu.lastname, mu.email from mdl_user as mu where mu.username = %s"
            cursor.execute(tempSQL, [cedula]) 
            result = cursor.fetchall()[0]
            return UserMoodle(userid=cedula, firstname=result[1], lastname=result[2], email=result[3])
        
    except IndexError:
        logger.error(f"Usuario {cedula} no encontrado en Moodle")
        return None
    except Exception as e:
        logger.error(f"Error al obtener el usuario {cedula} en Moodle: {str(e)}")
        raise e