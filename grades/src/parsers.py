from src.utils.moodle_client import MoodleClient
from src.grade_report_flow import get_course_grade_report
from src.utils.logging.logger_factory import get_logger

logger = get_logger()

TEMPLATE = "PLANTILLA"


def parse_category_path(
    category_id: int, moodle_client: MoodleClient
) -> tuple[str, str]:
    """
    Obtiene el path de categorías tanto por ID como por nombre.
    
    Args:
        category_id: ID de la categoría
        moodle_client: Cliente de Moodle
        
    Returns:
        tuple: (category_id_path, category_name_path)
    """
    category_info = moodle_client.get_category_info(category_id)
    category_id_path = category_info["path"]
    category_name_path = "/".join(
        moodle_client.get_category_info(int(id))["name"]
        for id in category_id_path.split("/") if id != ""
    )
    return category_id_path, category_name_path


def extract_period_from_category_path(category_name_path: str) -> str:
    """
    Extrae el período del path de categorías.
    Asume que el período está en la segunda posición del path.
    
    Args:
        category_name_path: Path de categorías separado por "/"
        
    Returns:
        str: Período extraído
    """
    try:
        categories = category_name_path.split("/")
        # Filtrar categorías vacías
        categories = [cat for cat in categories if cat.strip()]
        # El período suele estar en la segunda posición (index 1)
        if len(categories) > 1:
            return categories[1]
        return "N/A"
    except Exception as e:
        logger.error(f"Error extrayendo período de {category_name_path}: {e}")
        return "N/A"


def extract_course_grade_info(
    course_id: int, 
    course_shortname: str, 
    moodle_client: MoodleClient,
    ofg_pos: int
) -> list[dict]:
    """
    Extrae información completa de un curso incluyendo calificaciones.
    Devuelve una lista de diccionarios, cada uno representando una fila del Excel.
    
    Args:
        course_id: ID del curso en Moodle
        course_shortname: Nombre corto del curso
        moodle_client: Cliente de Moodle
        ofg_pos: Posición del OFG en el shortname (split por "-")
        
    Returns:
        list[dict]: Lista de filas para el Excel, cada diccionario es un estudiante con sus calificaciones
    """
    logger.info(f"Extrayendo información del curso {course_shortname}")
    
    try:
        # Obtener información básica del curso
        course = moodle_client.get_course_by_field("id", course_id)
        if not course:
            logger.warning(f"No se encontró el curso {course_id}")
            return []
        
        # Obtener path de categorías para extraer el período
        category_id_path, category_name_path = parse_category_path(
            course["categoryid"], moodle_client
        )
        
        # Extraer período
        periodo = extract_period_from_category_path(category_name_path)
        
        # Extraer OFG del shortname
        try:
            ofg = course_shortname.split("-")[ofg_pos]
        except IndexError:
            logger.warning(f"No se pudo extraer OFG de {course_shortname}")
            ofg = "N/A"
        
        # Obtener usuarios inscritos (estudiantes y docentes)
        enrolled_users = moodle_client.get_course_enrolled_users(course_id)
        
        # Extraer información del docente
        teachers = enrolled_users.get("teachers", [])
        if not teachers:
            logger.warning(f"Curso {course_shortname} no tiene profesor asignado")
            profesor_nombre = "SIN PROFESOR"
            profesor_cedula = "SIN PROFESOR"
        else:
            primer_docente = teachers[0]
            profesor_nombre = primer_docente.get("fullname", "SIN PROFESOR")
            profesor_cedula = primer_docente.get("username", "SIN PROFESOR")
        
        # Obtener reporte de calificaciones usando el método de grade_report_flow
        # Este método ya devuelve una lista de diccionarios con las calificaciones parseadas
        grades_list = get_course_grade_report(moodle_client, course_id)
        
        # Enriquecer cada fila con la información del curso y docente
        excel_rows = []
        for student_grades in grades_list:
            row = {
                "PERIODO": periodo,
                "OFG": ofg,
                "PROFESOR NOMBRE": profesor_nombre,
                "PROFESOR CEDULA": profesor_cedula,
                "NOMBRE": course_shortname,
                **student_grades  # Ya incluye ESTUDIANTE, CEDULA_ESTUDIANTE, CORTE_1, CORTE_2, etc.
            }
            excel_rows.append(row)
        
        logger.info(f"Información del curso {course_shortname} extraída exitosamente: {len(excel_rows)} estudiantes")
        return excel_rows
        
    except Exception as e:
        logger.error(f"Error extrayendo información del curso {course_shortname}: {e}")
        raise e

