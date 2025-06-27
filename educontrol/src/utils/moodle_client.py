import requests
from src.utils.logging.logger_factory import get_logger

logger = get_logger()

STUDENT_ROLE_ID = 5
TEACHER_ROLE_ID = 3



class MoodleClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self._base_params = {
            "wstoken": self.token,
            "moodlewsrestformat": "json"
        }

    def search_courses(self, criteria: str) -> list[dict]:
        try:
            params = {
                "wsfunction": "core_course_search_courses",
                "criterianame": "search",
                "criteriavalue": criteria
            }
            response = requests.get(self.url, params=self._base_params | params)
            response.raise_for_status()
            logger.info(f"Cursos con criterio {criteria} encontrados")
            if "exception" in response.json():
                logger.error(f"Error con Moodle: {str(response.json())}")   
# sourcery skip: raise-specific-error
                raise Exception(str(response.json()["exception"]))
            return response.json()["courses"]
        except Exception as e:
            logger.error(f"Error al buscar cursos con criterio {criteria}: {e}")
            raise e
    
    def get_course_by_field(self, field: str, value: str) -> dict:
        try:
            params = {
                "wsfunction": "core_course_get_courses_by_field",
                "field": field,
                "value": value
            }
            response = requests.get(self.url, params=self._base_params | params)
            response.raise_for_status()
            logger.info(f"Curso con {field} {value} encontrado")
            if "exception" in response.json():
# sourcery skip: extract-method, raise-specific-error
                raise Exception(f"Error con Moodle: {str(response.json())}")
            return response.json()["courses"][0]
        except IndexError:
            logger.error(f"No se encontró ningún curso con {field} {value}")
            return None
        except Exception as e:
            logger.error(f"Error al buscar curso con {field} {value}: {e}")
            raise e
        
    def _parse_enrolled_response(self, response: dict) -> dict:
        students = []
        teachers = []
        for user in response:
            if user["roles"][0]["roleid"] == STUDENT_ROLE_ID:
                students.append(user)
            elif user["roles"][0]["roleid"] == TEACHER_ROLE_ID:
                teachers.append(user)
        return {
            "students": students,
            "teachers": teachers
        }
    
    def get_course_enrolled_users(self, course_id: int) -> list[dict]:
        try:
            params = {
                "wsfunction": "core_enrol_get_enrolled_users",
                "courseid": course_id
            }
            response = requests.get(self.url, params=self._base_params | params)
            response.raise_for_status()
            logger.info(f"Usuarios inscritos en el curso {course_id} obtenidos")
            if "exception" in response.json():
                raise Exception(f"Error con Moodle: {str(response.json())}")
            return self._parse_enrolled_response(response.json())
        except Exception as e:
            logger.error(f"Error al obtener usuarios inscritos en el curso {course_id}: {e}")
            raise e
        
        
    def get_course_contents(self, course_id: int) -> dict:
        try:
            params = {
                "wsfunction": "core_course_get_contents",
                "courseid": course_id
            }
            response = requests.get(self.url, params=self._base_params | params)
            response.raise_for_status()
            logger.info(f"Contenidos del curso {course_id} obtenidos")
            if "exception" in response.json():
                raise Exception(f"Error con Moodle: {str(response.json())}")
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener contenidos del curso {course_id}: {e}")
            raise e
        
    def get_category_info(self, category_id: int, include_subcategories: bool = False) -> dict:
        try:
            params = {
                "wsfunction": "core_course_get_categories",
                'criteria[0][key]': 'id',                
                'criteria[0][value]': category_id,
                'addsubcategories': int(include_subcategories),
            }
            response = requests.get(self.url, params=self._base_params | params)
            response.raise_for_status()
            logger.info(f"Información de la categoría {category_id} obtenida")
            if "exception" in response.json():
                raise Exception(f"Error con Moodle: {str(response.json())}")
            return response.json()[0]
        except Exception as e:
            logger.error(f"Error al obtener información de la categoría {category_id}: {e}")
            raise e
        
    
        