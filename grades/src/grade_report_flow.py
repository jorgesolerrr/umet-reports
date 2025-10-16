from src.utils.moodle_client import MoodleClient

#
# {
#     "cedula": "1723074124",
#     "nombre": "Juan Perez",
#     "corte_x":
# }
#

def _parse_user_grade(user_grade_items: dict) -> dict:
    parcial = 0
    user_grades = {
        "ESTUDIANTE": user_grade_items["userfullname"],
        "CEDULA_ESTUDIANTE": user_grade_items["useridnumber"],
    }
    for grade_item in user_grade_items["gradeitems"]:
        if grade_item["itemtype"] == "category":
            parcial += 1
            user_grades[f"CORTE_{parcial}"] = grade_item["graderaw"] if grade_item["graderaw"] is not None else "SIN CALIFICACION"
    return user_grades
    
def get_course_grade_report(moodle_client: MoodleClient, course_moodle_id: int) -> list[dict]:
    grades = moodle_client.get_course_grade_report(course_moodle_id)
    user_grades = []
    for user_grade in grades:
        user_grades.append(_parse_user_grade(user_grade))
    return user_grades
        
    
    