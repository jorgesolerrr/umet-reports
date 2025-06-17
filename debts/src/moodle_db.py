from typing import Generator
from mysql.connector import connect, MySQLConnection
from .schemas import MoodleConn
from src.logging.logger_factory import get_logger

logger = get_logger()

def get_moodle_db(moodleConn: MoodleConn) -> Generator[MySQLConnection, None, None]:
    try:
        conn = connect(
            host=moodleConn.host,
            port=moodleConn.port,
            user=moodleConn.db_user,
            password=moodleConn.db_password,
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
    except Exception as e:
        logger.error(f"Error al actualizar el usuario {cedula} en Moodle: {e}")
        raise e