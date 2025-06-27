from src.utils.redis_client import RedisClient

# params example:
# {
#     "ofg-pos": -3,
#     ...
# }

def build_initial_data(course_info: dict, course_name: str, ofg_pos: int):
    data = {
        "OFG" : course_name.split("-")[ofg_pos],
        "id_curso" : course_info["courseid"],
        "Total_Secciones" : len(course_info["sections"]),    
        "Total_Estudiantes" : len(course_info["students"]),
        "Total_Docentes" : len(course_info["teachers"]),
        "Docentes" : ",".join(course_info["teachers"]) if (len(course_info["teachers"]) > 0) else "-",
    }
    for i, category in enumerate(course_info["coursePath"].split("/")):
        if category == "":
            continue
        data[f"Categoria_{i+1}"] = category
    return data


def 

def build_report_json(courses: list, redis_client: RedisClient, params: dict):
    period, course_name, _ = course_key.split(":")
    result = []
    
    for course_key in courses:
        course_info = redis_client.get_hset(course_key)
        
        
    return report
    





