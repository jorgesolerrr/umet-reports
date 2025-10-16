"""
Proyecto Grades - Reportes de Calificaciones
"""

from src.utils.logging.logger_factory import setup_logging
from src.extract_data_flow import extract_grades_data_flow
from src.build_report import get_grades_data, make_grades_report
from src.utils.redis_client import RedisClient
from src.settings import settings
import pandas as pd


def main():
    """
    Función principal que orquesta todo el flujo de extracción y reporte de calificaciones.
    """
    # Inicializar logging
    setup_logging()
    
    # Crear cliente de Redis
    redis_client = RedisClient()
    
    # Extraer datos de calificaciones de Moodle en paralelo
    extract_grades_data_flow(
        moodle_url=settings.MOODLE_URL,
        moodle_token=settings.MOODLE_TOKEN,
        moodle_name=settings.MOODLE_NAME,
        patterns=settings.COURSE_PATTERNS,
        ofg_pos=settings.OFG_POS,
        max_workers=8
    )
    
    # Obtener datos de Redis (ya vienen las filas completas del Excel)
    excel_data = get_grades_data(redis_client, settings.COURSE_PATTERNS)
    
    # Generar archivo Excel
    timestamp = pd.Timestamp.now().strftime('%Y%m%d')
    filename = f"reporte_calificaciones_{timestamp}.xlsx"
    make_grades_report(excel_data, filename=filename)
    
    # Limpiar Redis
    redis_client.client.flushall()
    
    print(f"Reporte generado exitosamente: {filename}")


if __name__ == "__main__":
    main()

