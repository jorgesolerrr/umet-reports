import schedule
import time
import signal
import sys
from src.utils.mailer import send_userNotification
from src.tasks import disable_users, enable_users
from src.logging.logger_factory import setup_logging, get_logger
from src.db import get_db, get_available_lms, get_suspended_users_info_by_lms
from src.moodle_db import get_moodle_db
from src.utils.sna_api import call_sna_api_deudas, _filter_response
from src.build_report import build_report
from src.settings import settings
import pandas as pd

logger = get_logger()

USERS = [
    {
        "userName": "Jorge Soler",
        "userEmail": "jsoler@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Dirección General",
        "userEmail": "direcciongeneral@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Contador General",
        "userEmail": "contadorgeneral@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Orientador 3Gye",
        "userEmail": "orientador3gye@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Orientador Gye3",
        "userEmail": "orientadorgye3@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Orientador 3UIO",
        "userEmail": "orientadoruio3@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "Orientador 2UIO",
        "userEmail": "orientadoruio2@umet.edu.ec",
        "lmsName": "UMET",
    },
    {
        "userName": "llondono",
        "userEmail": "llondono@umet.edu.ec",
        "lmsName": "UMET",
    }
]


def DebtsSentinel():
    db = next(get_db())
    available_lms = get_available_lms(db)
    debt_users = call_sna_api_deudas()
    report = build_report(debt_users)
    for user in USERS:
        try:
            send_userNotification(settings.REPORT_NOTIFICATION, user, [report])
            logger.info(f"Reporte enviado a {user['userName']}")
        except Exception as e:
            logger.error(f"Error al enviar reporte a {user['userName']}: {e}")
            continue
        time.sleep(1)
    for lms in available_lms:
        SNA_userList_set, SNA_userListProg = _filter_response(
            debt_users, lms.db_programs.split(",")
        )
        try:
            moodleConn = next(get_moodle_db(lms))
        except Exception as e:
            logger.error(f"Error al obtener conexión a Moodle: {e}")
            continue

        try:
            disable_users(
                moodleConn, db, lms.lms_name, SNA_userList_set, SNA_userListProg
            )
        except Exception as e:
            logger.error(f"Error al habilitar usuarios: {e}")
            continue
        try:
            enable_users(
                moodleConn, db, lms.lms_name, SNA_userList_set, SNA_userListProg
            )
        except Exception as e:
            logger.error(f"Error al deshabilitar usuarios: {e}")
            continue


def signal_handler(sig, frame):
    """Maneja la señal de interrupción para terminar el programa limpiamente"""
    logger.info("Recibida señal de interrupción. Terminando programa...")
    sys.exit(0)


def run_sentinel():
    """Wrapper para ejecutar DebtsSentinel con manejo de excepciones"""
    try:
        logger.info("Iniciando ejecución del Sentinel de Deudas...")
        DebtsSentinel()
        logger.info("Ejecución del Sentinel de Deudas completada exitosamente")
    except Exception as e:
        logger.error(f"Error durante la ejecución del Sentinel de Deudas: {e}")


def main():
    setup_logging()
    logger.info("Iniciando servicio de monitoreo de deudas...")

    # Configurar manejo de señales para terminar limpiamente
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Programar la tarea para que se ejecute cada 60 minutos
    schedule.every(settings.MINUTES_TO_RUN).minutes.do(run_sentinel)

    # Ejecutar inmediatamente al inicio
    logger.info("Ejecutando primera verificación...")
    run_sentinel()

    # Loop principal para mantener el programa corriendo
    logger.info(f"Servicio iniciado. Próxima ejecución en {settings.MINUTES_TO_RUN} minutos...")
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def main2():
    db = next(get_db())
    suspended_users = get_suspended_users_info_by_lms(db, "CESDEL-POST(NEW)")
    df_data = []
    df_data.extend(
        {
            "fecha": user[0].strftime("%Y-%m-%d"),
            "cedula": user[1],
            "programa": user[2],
            "deuda1": user[3].split(",")[0],
            "deuda2": user[3].split(",")[1],
        }
        for user in suspended_users
    )
    df = pd.DataFrame(df_data)
    print(df)
    df.to_excel("suspended_post_users.xlsx", index=False)


if __name__ == "__main__":
    main()
