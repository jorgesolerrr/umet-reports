import requests
from src.utils.logging.logger_factory import get_logger

logger = get_logger()

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
                raise Exception(str(response.json()))
            return response.json()
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
# sourcery skip: raise-specific-error
                raise Exception(f"Error con Moodle: {str(response.json())}")
            return response.json()
        except Exception as e:
            logger.error(f"Error al buscar curso con {field} {value}: {e}")
            raise e
        