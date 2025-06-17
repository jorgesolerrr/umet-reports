from debts.src.tasks import disable_users, enable_users
from src.logging.logger_factory import setup_logging, get_logger
from src.db import get_db, get_available_lms
from src.moodle_db import get_moodle_db
from src.utils.sna_api import call_sna_api_deudas, _filter_response

logger = get_logger()

def DebtsSentinel():
    db = next(get_db())
    available_lms = get_available_lms(db)
    debt_users = call_sna_api_deudas()
    for lms in available_lms:
        SNA_userList_set, SNA_userListProg = _filter_response(debt_users, lms.db_programs.split(","))
        try:
            moodleConn = get_moodle_db(lms)
        except Exception as e:
            logger.error(f"Error al obtener conexión a Moodle: {e}")
            continue
        
        try:
            disable_users(moodleConn, db, lms.lms_name, SNA_userList_set, SNA_userListProg)
        except Exception as e:
            logger.error(f"Error al habilitar usuarios: {e}")
            continue
        try:
            enable_users(moodleConn, db, lms.lms_name, SNA_userList_set, SNA_userListProg)
        except Exception as e:
            logger.error(f"Error al deshabilitar usuarios: {e}")
            continue
        
        
    

def main():
    setup_logging()
    debt_users = call_sna_api_deudas(["GRADO", "UAFTT"])
    print(debt_users)
    

if __name__ == "__main__":
    main()