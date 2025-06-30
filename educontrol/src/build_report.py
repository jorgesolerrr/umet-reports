import json

from src.utils.redis_client import RedisClient
from src.utils.logging.logger_factory import get_logger

logger = get_logger()
def get_courses_data(redis_client: RedisClient):
    result_contentTotals = []
    result_modulesIndexes = {}
    logger.info(f"Getting courses data from redis {redis_client.client.llen('contentTotals')}")
    while redis_client.client.llen("contentTotals") > 0:
        slice_contentTotals_i = json.loads(redis_client.client.lpop("total_report_json"))
        slice_moduleIndexes_i = json.loads(redis_client.client.lpop("module_indexes"))
        result_contentTotals.extend(slice_contentTotals_i)
        result_modulesIndexes.update(slice_moduleIndexes_i)
    return result_contentTotals, result_modulesIndexes

def MakeQuantitativeReport(redis_client: RedisClient):
    rep_content, modulesIndexes = get_courses_data(redis_client)
    logger.info("Iniciando reporte cuantitativo")
    courses_withoutTeacher = []
    courses_withProblems = []
    excel_rep = []
    for course in rep_content:
        if course["NoDocentes"] == 0:
            courses_withoutTeacher.append(course["Nombre"])
            continue
        profesor = course["Docentes"].split(",")[0]
        try:
            row = {
                "PLATAFORMA" : course["categ_1"],
                "FACULTAD" : course["categ_3"],
                "PERIODO" : course["categ_2"],
                "CARRERA" : course["categ_4"],
                "TIPO APROBACION" : course["categ_5"],
                "PROFESOR NOMBRE" : profesor.split(":")[1],
                "PROFESOR CEDULA" : profesor.split(":")[0],
                "NOMBRE" : course["Nombre"],
                "OFG" : int(course["OFG"]),
                "CANT_ESTUDIANTES" : course["NoEstudiantes"],
                "secciones": course["NoSecciones"],
                #!arreglar esto, poner las secciones que se van a tener en cuenta en una lista
                "links_clases": course["T_links_clases"],
                "links": course["T_links"],
                "archivos": course["T_archivos"],
                "labels":course["T_label"],
                "pags": course["T_pags"],
                "libros": course["T_libros"],
                "TOTAL_RECURSOS" : course["T_links_clases"] + course["T_links"] + course["T_archivos"] + course["T_label"] + course["T_pags"] + course["T_libros"],
                "tareas": course["T_tareas"],
                "quiz": course["T_quiz"], 
                "glosario": course["T_glosario"],
                "taller": course["T_taller"],
                "leccion": course["T_leccion"],
                "foro": course["T_foro"],
                "wiki": course["T_wiki"],
                "chat": course["T_chat"],
                "mapaMental": course["T_mapaMental"],
                "TOTAL_ACTIVIDADES" : course["T_tareas"] + course["T_quiz"] + course["T_glosario"] +
                course["T_taller"] + course["T_leccion"] + course["T_foro"] + course["T_wiki"] + course["T_chat"] + course["T_mapaMental"]
            }
            excel_rep.append(row)
        except Exception as e:
            print(course["OFG"] + ": ------> " + str(e))
            courses_withProblems.append(course["Nombre"])
            continue
        del row
    logger.info("Reporte cuantitativo finalizado")
    return {
        "excel" : excel_rep, 
        "SIN PROFESORES" : courses_withoutTeacher,
        "CON PROBLEMAS" : courses_withProblems
    }