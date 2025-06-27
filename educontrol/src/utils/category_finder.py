from abc import ABC, abstractmethod

class CategoryBuilder(ABC):
    @abstractmethod
    def build_categories(self, course_data: dict) -> dict:
        pass



class GradeCategoryBuilder(CategoryBuilder):
    def build_categories(self, course_data: dict) -> dict:
        return {
            "PLATAFORMA" : course_data["Categoria_1"],
            "FACULTAD" : course_data["Categoria_3"],
            "PERIODO" : course_data["Categoria_2"],
            "CARRERA" : course_data["Categoria_4"],
            "TIPO APROBACION" : course_data["Categoria_5"]
        }

    
class PostCategoryBuilder(CategoryBuilder):
    def build_categories(self, course_data: dict) -> dict:
        return {
            "PLATAFORMA" : course_data["Categoria_1"],
            "FACULTAD" : course_data["Categoria_2"],
            "AÑO" : course_data["Categoria_3"],
            "CARRERA" : course_data["Categoria_4"],
            "GRUPO" : course_data["Categoria_5"],
            "TIPO APROBACION" : course_data["Categoria_6"]
        }
