from abc import ABC, abstractmethod

class CategoryFinder(ABC):
    @abstractmethod
    def find_category(self, course_id: int) -> int:
        pass



        