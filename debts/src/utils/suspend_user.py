from src.logging.logger_factory import get_logger
from mysql.connector import MySQLConnection
from src.db import post_suspended_user, delete_suspended_user
from src.moodle_db import path_moodle_user
from src.utils.mailer import send_userNotification
from src.settings import settings


logger = get_logger()

ENV = "PRODUCCION"

def suspend_user(lmsName: str, user: dict, moodleConn: MySQLConnection, gwDB: MySQLConnection):
    # 1 -> Registrar en tbSuspended
    post_suspended_user(gwDB, lmsName, user)
    logger.info(f"Usuario {user['cedula']} suspendido")

    # 2 -> Modificar en moodle el estado de suspended a 1
    userMoodle = path_moodle_user(moodleConn, cedula=user["cedula"], suspended=True)
    if userMoodle is None:
        raise ValueError(f"Error al suspender usuario {user['cedula']} en Moodle")

    user |= {
        "userName": f"{userMoodle.firstname} {userMoodle.lastname}",
        "userEmail": userMoodle.email,
        "lmsName": lmsName,
    }
    # only for debugging purposes
    match ENV:
        case "DESARROLLO":
            user["userEmail"] = "jsoler@umet.edu.ec"
        case "PRODUCCION":
            pass
        case _:
            logger.error("Error: Revisar nomenclatura del entorno de trabajo.")
            raise ValueError(
                "Error: Revisar nomenclatura del entorno de trabajo."
            )

    send_userNotification(settings.SUSPENDED_NOTIFICATION, user)

def activate_user(lmsName: str, user: dict, moodleConn: MySQLConnection, gwDB: MySQLConnection):
    
    # proceder a habilitar al usuario
    # 1 -> Eliminar registro en tbSuspended
    delete_suspended_user(gwDB, lmsName, user)
    logger.info(f"Usuario {user['cedula']} activado")

    # 2 -> Modificar en moodle el estado de suspended a 0
    userMoodle = path_moodle_user(moodleConn, user["cedula"], suspended=False)
    logger.info(f"Usuario {user['cedula']} activado en Moodle")

    user |= {
        "userName": f"{userMoodle.firstname} {userMoodle.lastname}",
        "userEmail": userMoodle.email,
        "lmsName": lmsName,
    }
    # only for debugging purposes            
    match ENV:
        case "DESARROLLO":
            user["userEmail"] = "jsoler@umet.edu.ec"
        case "PRODUCCION":
            pass
        case _:
            logger.error("Error: Revisar nomenclatura del entorno de trabajo.")
            raise ValueError(
                "Error: Revisar nomenclatura del entorno de trabajo."
            )

    send_userNotification(settings.ACTIVATED_NOTIFICATION, user)
    logger.info(f"Usuario {user['cedula']} activado")