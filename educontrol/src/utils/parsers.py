from src.utils.moodle_client import MoodleClient
from src.utils.logging.logger_factory import get_logger

fields = [
    "id",
    "shortname",
    "startDate",
    "endDate",
    "categoryid",
    "numsections",
    "timecreated",
    "timemodified",
    "visible",
]

URL = ["url"]
RESOURCES = ["url", "resource", "folder"]

logger = get_logger()

GRADO = "CESDEL-CARRERAS(NEW)"


def parse_category_path(
    category_id: int, moodle_client: MoodleClient
) -> tuple[str, str]:
    category_info = moodle_client.get_category_info(category_id)
    category_id_path = category_info["path"]
    category_name_path = "/".join(
        moodle_client.get_category_info(int(id))["name"]
        for id in category_id_path.split("/") if id != ""
    )
    return category_id_path, category_name_path


def parse_course_sections(sections: list) -> dict:
    return [
        {
            "sectionId": section["id"],
            "sectionNo": section["section"],
            "sectionName": section["name"],
            "sectionVisible": section["visible"],
            "modules": parse_section_modules(section["modules"]),
        }
        for section in sections
    ]


def parse_section_modules(modules: list) -> dict:
    data = []
    for module in modules:
        module_data = {
            "moduleid": module["id"],
            "moduleName": module["name"],
            "moduleType": module["modname"],
            "moduleInstance": module["instance"],
            "moduleVisible": module["visible"],
            "completion": module["completion"],
            "dates": module["dates"],
            "url": module["url"] if (module["modname"] in URL) else "",
        }
        if module["modname"] in RESOURCES:
            module_data["c_info_filesCount"] = module["contentsinfo"]["filescount"]
            module_data["c_info_filesSize"] = module["contentsinfo"]["filessize"]
            module_data["c_info_lastmodified"] = module["contentsinfo"]["lastmodified"]
            module_data["contents"] = parse_moodle_contents(module["contents"])
        data.append(module_data)
    return data

def parse_moodle_contents(contents: list) -> dict:
    return [
        {
            "cont_Type": content["type"],
            "cont_Name": content["filename"],
            "cont_fsize": content["filesize"],
            "cont_fileurl": content["fileurl"],
            "cont_timemodified": content["timemodified"],
            "cont_userId": content["userid"],
            "cont_author": content["author"],
        }
        for content in contents
    ]


def extract_course_info(course_id: int, moodle_client: MoodleClient) -> dict:
    logger.info(f"Extrayendo información del curso {course_id}")
    course = moodle_client.get_course_by_field("id", course_id)
    if not course:
        return None
    data = {
        key: value for key, value in course.items() if key in fields
    }
    data["category_id_path"], data["category_name_path"] = parse_category_path(data["categoryid"], moodle_client)
    data |= moodle_client.get_course_enrolled_users(course_id)
    data["sections"] = parse_course_sections(moodle_client.get_course_contents(course_id))
    #if moodle_client.name == GRADO:
        #grade_report = [] #moodle_client.get_course_grade_report(course_id)
        #data["grade_report"] = grade_report #parse_grade_report(grade_report)
    logger.info(f"Información del curso {course_id} extraída")
    
    return data
    

def parse_grade_report(grade_report: list) -> dict:
    grade_categories = {}
    for grade_item in grade_report:
        if grade_item["categoryid"]:
            value = grade_categories.setdefault(grade_item["categoryid"], [])
            if grade_item["itemtype"] == "mod" and not grade_item["gradeishidden"]:
                value.append(grade_item)
        
    return parse_grade_categories(grade_categories)
    
    
def parse_grade_categories(grade_categories: dict) -> dict:
    final_grade_categories = {}
    keys = grade_categories.keys()
    for i, grade_category in enumerate(keys):
        if i == len(keys)-1:
            final_grade_categories["corte-final"] = len(grade_categories[grade_category])
        else:
            final_grade_categories[f"corte-parcial-{i+1}"] = len(grade_categories[grade_category])
    return final_grade_categories
        
    
    
    
    