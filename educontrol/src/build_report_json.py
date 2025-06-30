from src.utils.redis_client import RedisClient
import datetime

from src.utils.logging.logger_factory import get_logger

logger = get_logger()
# params example:
# {
#     "ofg-pos": -3,
#     ...
# }

MODULE_TYPES = {
    "url" : "links",
    "resource" : "archivos",
    "page" : "pags",
    "book" : "libros",
    "assign" : "tareas",
    "quiz" : "quiz",
    "glossary" : "glosario",
    "workshop" : "taller",
    "lesson" : "leccion",
    "forum" : "foro",
    "wiki" : "wiki",
    "chat" : "chat",
    "mindmap" : "mapaMental",
    "label" : "label",
    "videotime" : "video",
    "pdfannotator" : "archivos"
}

ACTIVITY_TYPES = [
    "assign",
    "quiz",
    "glossary",
    "workshop",
    "lesson",
    "forum",
    "wiki",
    "chat",
    "mindmap",
]


def build_initial_data(course_info: dict, course_name: str, ofg_pos: int):
    data = {
        "OFG": course_name.split("-")[ofg_pos],
        "course_name": course_name,
        "id_curso": course_info["id"],
        "Total_Secciones": len(course_info["sections"]),
        "Total_Estudiantes": len(course_info["students"]),
        "Total_Docentes": len(course_info["teachers"]),
        "Docentes": (
            ",".join(
                [f"{teacher['fullname']}:{teacher['username']}" for teacher in course_info["teachers"]]
            )
            if len(course_info["teachers"]) > 0
            else "-"
        ),
    }
    for i, category in enumerate(course_info["category_name_path"].split("/")):
        if category == "":
            continue
        data[f"Categoria_{i+1}"] = category

    data |={
            # Recursos 
            "Existe_PEA": 0,
            "Existe_Guia": 0,
            "Existe_CV": 0,            
            "T_links_clases": 0, "T_links": 0, "T_archivos": 0, "T_pags": 0, "T_libros": 0,
            # Actividades interactivas
            "T_tareas": 0, "T_quiz": 0, "T_glosario": 0, "T_chat": 0, "T_taller" : 0, "T_leccion" : 0, 
            "T_foro" : 0, "T_wiki": 0, "T_mapaMental": 0, "T_label": 0, "T_video": 0,
            "T_actividades_abiertas": 0,
            "NoSecciones": len(course_info["sections"])            
        }
    return data


def build_course_report(course_info: dict, course_name: str, ofg_pos: int):
    logger.info(f"Building course report for {course_name}")
    course_data = build_initial_data(course_info, course_name, ofg_pos)
    module_indexes = {}
    for section_index, section_info in enumerate(course_info["sections"]):
        logger.info(f"Building section report for {course_name} - {section_info['sectionName']}")
        try:
            build_section_report(section_info, section_index, course_data, module_indexes)
        except Exception as e:
            logger.error(f"Error building section report for {course_name} - {section_info['sectionName']}: {e}")
            continue
    logger.info(f"Course report for {course_name} built")
    return course_data, module_indexes

def build_section_report(section_info: dict, section_index: int, course_data: dict, module_indexes: dict):
    
    course_data  |= {
        f"S{section_index}_id": section_info["sectionId"], f"S{section_index}_No": section_info["sectionNo"], 
        f"S{section_index}_Nombre": section_info["sectionName"],                
        f"S{section_index}_links_clases": 0,    f"S{section_index}_links": 0,       
        f"S{section_index}_archivos": 0,        f"S{section_index}_pags": 0,        
        f"S{section_index}_libros": 0,          f"S{section_index}_tareas": 0,
        f"S{section_index}_quiz": 0,            f"S{section_index}_glosario": 0,
        f"S{section_index}_taller": 0,          f"S{section_index}_leccion": 0,     
        f"S{section_index}_foro": 0,            f"S{section_index}_wiki": 0,            
        f"S{section_index}_chat": 0,            f"S{section_index}_mapaMental": 0,
        f"S{section_index}_label": 0,           f"S{section_index}_video": 0,
        f"S{section_index}_actividades_abiertas": 0,
    }
    if section_info["sectionVisible"] != 1:
        return None
    for module_info in section_info["modules"]:
        try:
            build_module_report(module_info, course_data, section_index, course_data["OFG"], module_indexes)
        except Exception as e:
            logger.error(f"Error building module report for {course_data['course_name']} - {module_info['moduleName']}: {e}")
            continue
    
def build_module_report(module_info: dict, course_data : dict, section_index: int, ofg: str, module_indexes: dict):
    if module_info["moduleVisible"] != 1:
        return None
    if module_info["moduleType"] == "forum" and module_info["moduleName"] == "Avisos":
        return None

    if module_info["moduleType"] in ACTIVITY_TYPES and len(module_info["dates"]) > 1:
        
        activity_end_date = datetime.date.fromtimestamp(module_info["dates"][1]["timestamp"])
        if activity_end_date > datetime.date.today():
            course_data[f"S{section_index}_actividades_abiertas"] += 1
            course_data["T_actividades_abiertas"] += 1
            return

    if module_info["moduleType"] == "url" and len(module_info["contents"]) > 0:
        fileurl = module_info["contents"][0]["cont_fileurl"]
        if "https://www.youtube.com/ejemplo.mov" in fileurl:
            return
        if "https://umeteduec.sharepoint.com" in fileurl and ofg in fileurl:
            course_data[f"S{section_index}_links_clases"] += 1
            course_data["T_links_clases"] += 1
        else:
            course_data[f"S{section_index}_links"] += 1
            course_data["T_links"] += 1
        return

    if module_info["moduleType"] == "folder":
        course_data[f"S{section_index}_archivos"] += len(module_info["contents"])
        course_data["T_archivos"] += len(module_info["contents"])
        return

    if module_info["moduleType"] == "resource":
        course_data[f"S{section_index}_archivos"] += len(module_info["contents"])
        course_data["T_archivos"] += len(module_info["contents"])
        name = module_info["moduleName"]
        if ("Syllabus de la Asignatura" in name or "PEA" in name) and len(module_info["contents"]) > 0:
            course_data["Existe_PEA"] = 1
        elif ("Curriculum" in name or "Hoja de vida" in name) and len(module_info["contents"]) > 0:
            course_data["Existe_CV"] = 1
        elif "Guía de Estudio" in name and len(module_info["contents"]) > 0:
            course_data["Existe_Guia"] = 1
        return

    module_type = MODULE_TYPES[module_info["moduleType"]]
    course_data[f"S{section_index}_{module_type}"] += 1
    course_data[f"T_{module_type}"] += 1
    module_indexes[module_info["moduleid"]] = {
        "sectionID": section_index,
        "courseID": course_data["id_curso"],
        "courseName": course_data["course_name"],
    }
    return