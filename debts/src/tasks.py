from mysql.connector import MySQLConnection
from debts.src.db import get_suspended_users, get_db
from debts.src.schemas import MoodleConn
from debts.src.utils.suspend_user import activate_user, suspend_user
from src.logging.logger_factory import get_logger

logger = get_logger()

def disable_users(
    moodleConn : MoodleConn,
    db: MySQLConnection,
    lmsName: str,
    SNA_userList_set: set, 
    SNA_userListProg: list
):    
    
    try:
        #Traer de gwDB, tabla tbSuspended, los usuarios con deuda activa. Retorna conjunto de cédulas. (set) 
        tbSuspended_set = get_suspended_users(db, lmsName)
        
        morosos_set = SNA_userList_set - tbSuspended_set
        morosos_list = [user for user in SNA_userListProg if user["cedula"] in morosos_set]
        
        if not morosos_list:
            logger.info("Ya todos los estudiantes con deuda tienen su cuenta suspendida")
            return "Ya todos los estudiantes con deuda tienen su cuenta suspendida"
        
        for user in morosos_list:
            try: 
                suspend_user(lmsName, user, moodleConn, db)
            except Exception as e:
                logger.error(f"Error al suspender usuario {user['cedula']}: {e}")
                continue
            
    except Exception as e:
        logger.error(f"Error al suspender usuarios: {e}")
        raise e


def enable_users(
    moodleConn : MoodleConn,
    db: MySQLConnection,
    lmsName: str,
    SNA_userList_set: set, 
    SNA_userListProg: list
):
    try:
        tbSuspended_set = get_suspended_users(db, lmsName)
        
        activos_set = tbSuspended_set - SNA_userList_set
        activos_list = [user for user in SNA_userListProg if user["cedula"] in activos_set]
        
        if not activos_list:
            logger.info("Ya todos los estudiantes con deuda tienen su cuenta activada")
            return "Ya todos los estudiantes con deuda tienen su cuenta activada"
        
        for user in activos_list:
            try:
                activate_user(lmsName, user, moodleConn, db)
            except Exception as e:
                logger.error(f"Error al activar usuario {user['cedula']}: {e}")
                continue
            
    except Exception as e:
        logger.error(f"Error al activar usuarios: {e}")
        raise e