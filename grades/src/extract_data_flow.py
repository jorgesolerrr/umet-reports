from collections.abc import Callable
from src.utils.moodle_client import MoodleClient
from src.utils.redis_client import RedisClient
from src.parsers import extract_course_grade_info
from src.utils.logging.logger_factory import get_logger
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import math

logger = get_logger()

TEMPLATE = "PLANTILLA"


def process_course(
    course: Dict[Any, Any],
    pattern: str,
    moodle_url: str,
    moodle_token: str,
    moodle_name: str,
    ofg_pos: int,
    redis_client: RedisClient,
) -> bool:
    """
    Procesa un curso individual extrayendo su información de calificaciones y guardándola en Redis.

    Args:
        course: Diccionario con información del curso
        pattern: Patrón de búsqueda usado
        moodle_url: URL de Moodle
        moodle_token: Token de Moodle
        moodle_name: Nombre de la instancia de Moodle
        ofg_pos: Posición del OFG en el shortname
        redis_client: Cliente de Redis

    Returns:
        bool: True si el curso fue procesado exitosamente, False en caso contrario
    """
    if TEMPLATE in course["shortname"]:
        return False

    logger.info(f"Extrayendo calificaciones del curso {course['shortname']}")

    try:
        moodle_client = MoodleClient(moodle_url, moodle_token, moodle_name)
        # extract_course_grade_info ahora devuelve una lista de filas (diccionarios) para el Excel
        excel_rows = extract_course_grade_info(
            course["id"], course["shortname"], moodle_client, ofg_pos
        )
        
        if excel_rows:
            # Guardamos las filas completas en Redis
            redis_key = f"{pattern}:{course['shortname']}:{datetime.now().strftime('%Y-%m-%d')}"
            redis_client.save_hset(redis_key, {"excel_rows": excel_rows})
            logger.info(f"Calificaciones del curso {course['shortname']} guardadas en Redis ({len(excel_rows)} filas)")
            return True
    except Exception as e:
        logger.error(f"Error procesando curso {course['shortname']}: {str(e)}")

    return False


def process_courses_chunk(
    courses_chunk: List[Dict[Any, Any]], 
    pattern: str, 
    moodle_url: str,
    moodle_token: str,
    moodle_name: str,
    ofg_pos: int
) -> int:
    """
    Procesa un chunk/lote de cursos.

    Args:
        courses_chunk: Lista de cursos a procesar
        pattern: Patrón de búsqueda usado
        moodle_url: URL de Moodle
        moodle_token: Token de Moodle
        moodle_name: Nombre de la instancia de Moodle
        ofg_pos: Posición del OFG en el shortname

    Returns:
        int: Número de cursos procesados exitosamente
    """
    redis_client = RedisClient()
    return sum(
        int(process_course(course, pattern, moodle_url, moodle_token, moodle_name, ofg_pos, redis_client))
        for course in courses_chunk
    )


def split_data_into_chunks(
    data: List[Dict[Any, Any]], num_chunks: int
) -> List[List[Dict[Any, Any]]]:
    """
    Divide la lista de cursos en chunks para procesamiento paralelo.

    Args:
        data: Lista completa de datos
        num_chunks: Número de chunks deseados

    Returns:
        List[List]: Lista de chunks, cada uno conteniendo una porción de datos
    """
    if not data:
        return []

    chunk_size = math.ceil(len(data) / num_chunks)
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def process_data(data: list, workers: int, process_func: Callable, *args):
    """
    Procesa datos en paralelo usando ThreadPoolExecutor.
    
    Args:
        data: Lista de datos a procesar
        workers: Número de workers
        process_func: Función de procesamiento
        *args: Argumentos adicionales para la función de procesamiento
        
    Returns:
        int: Total de elementos procesados
    """
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
        f"Procesamiento completado. Total procesados: {total_processed}"
    )
    return total_processed


def extract_grades_data_flow(
    moodle_url: str,
    moodle_token: str,
    moodle_name: str,
    patterns: List[str],
    ofg_pos: int,
    max_workers: int = 4
):
    """
    Extrae información de calificaciones de cursos de Moodle de forma paralela.

    Args:
        moodle_url: URL de Moodle
        moodle_token: Token de Moodle
        moodle_name: Nombre de la instancia de Moodle
        patterns: Lista de patrones de búsqueda
        ofg_pos: Posición del OFG en el shortname
        max_workers: Número máximo de workers para procesamiento paralelo
    """
    moodle_client = MoodleClient(moodle_url, moodle_token, moodle_name)

    for pattern in patterns:
        logger.info(f"Extrayendo información de los cursos con patrón {pattern}")
        courses = moodle_client.search_courses(pattern)
        
        if not courses:
            logger.info(f"No se encontraron cursos para el patrón {pattern}")
            continue
            
        # Filtrar cursos template antes de dividir en chunks
        filtered_courses = [
            course for course in courses if TEMPLATE not in course["shortname"]
        ]
        
        if not filtered_courses:
            logger.info(
                f"No se encontraron cursos válidos (sin plantillas) para el patrón {pattern}"
            )
            continue

        logger.info(
            f"Procesando {len(filtered_courses)} cursos en paralelo con {max_workers} workers"
        )
        process_data(
            filtered_courses, 
            max_workers, 
            process_courses_chunk, 
            pattern,
            moodle_url,
            moodle_token,
            moodle_name,
            ofg_pos
        )

