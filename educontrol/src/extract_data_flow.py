from collections.abc import Callable
from src.utils.moodle_client import MoodleClient
from src.utils.redis_client import RedisClient
from src.utils.parsers import extract_course_info
from src.utils.logging.logger_factory import get_logger
from src.schemas import MoodleAPIConn
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import math

logger = get_logger()

TEMPLATE = "PLANTILLA"


def process_course(
    course: Dict[Any, Any],
    period: str,
    moodle_client: MoodleClient,
    redis_client: RedisClient,
) -> bool:
    """
    Procesa un curso individual extrayendo su información y guardándola en Redis.

    Args:
        course: Diccionario con información del curso
        period: Período académico
        moodle_client: Cliente de Moodle
        redis_client: Cliente de Redis

    Returns:
        bool: True si el curso fue procesado exitosamente, False en caso contrario
    """
    if TEMPLATE in course["shortname"]:
        return False

    logger.info(f"Extrayendo información del curso {course['shortname']}")

    try:
        if course_info := extract_course_info(course["id"], moodle_client):
            redis_client.save_hset(
                f"{period}:{course['shortname']}:{datetime.now().strftime('%Y-%m-%d')}",
                course_info,
            )
            logger.info(f"Información del curso {course['shortname']} extraída")
            return True
    except Exception as e:
        logger.error(f"Error procesando curso {course['shortname']}: {str(e)}")

    return False


def process_courses_chunk(
    courses_chunk: List[Dict[Any, Any]], period: str, moodle_api_conn: MoodleAPIConn
) -> int:
    """
    Procesa un chunk/lote de cursos.

    Args:
        courses_chunk: Lista de cursos a procesar
        period: Período académico
        moodle_api_conn: Configuración de conexión a Moodle

    Returns:
        int: Número de cursos procesados exitosamente
    """
    moodle_client = MoodleClient(moodle_api_conn.url, moodle_api_conn.token)
    redis_client = RedisClient()
    return sum(
        int(process_course(course, period, moodle_client, redis_client))
        for course in courses_chunk
    )


def split_data_into_chunks(
    data: List[Dict[Any, Any]], num_chunks: int
) -> List[List[Dict[Any, Any]]]:
    """
    Divide la lista de cursos en chunks para procesamiento paralelo.

    Args:
        courses: Lista completa de cursos
        num_chunks: Número de chunks deseados

    Returns:
        List[List]: Lista de chunks, cada uno conteniendo una porción de cursos
    """
    if not data:
        return []

    chunk_size = math.ceil(len(data) / num_chunks)
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def extract_courses_data_flow(moodle_api_conn: MoodleAPIConn, max_workers: int = 4):
    """
    Extrae información de cursos de Moodle de forma paralela.

    Args:
        moodle_api_conn: Configuración de conexión a Moodle
        max_workers: Número máximo de workers para procesamiento paralelo
    """
    moodle_client = MoodleClient(moodle_api_conn.url, moodle_api_conn.token)

    for period in moodle_api_conn.periods:
        logger.info(f"Extrayendo información de los cursos del periodo {period}")
        courses = moodle_client.search_courses(period)
        if not courses:
            logger.info(f"No se encontraron cursos para el periodo {period}")
            continue
        # Filtrar cursos template antes de dividir en chunks
        filtered_courses = [
            course for course in courses if TEMPLATE not in course["shortname"]
        ]
        if not filtered_courses:
            logger.info(
                f"No se encontraron cursos válidos (sin plantillas) para el periodo {period}"
            )
            continue

        logger.info(
            f"Procesando {len(filtered_courses)} cursos en paralelo con {max_workers} workers"
        )
        process_data(filtered_courses, max_workers, process_courses_chunk, period, moodle_api_conn)
        


def process_data(data: list, workers : int, process_func: Callable, *args):
    chunks = split_data_into_chunks(data, workers)
    total_processed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_chunk = {
            executor.submit(process_func, chunk, *args): chunk
            for chunk in chunks
        }
        for future in as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                processed_count = future.result()
                total_processed += processed_count
                logger.info(f"Chunk completado: {processed_count} elementos procesados")
            except Exception as e:
                logger.error(f"Error procesando chunk: {str(e)}")
    logger.info(
        f"Información procesada. Total procesados: {total_processed}"
    )
    return total_processed