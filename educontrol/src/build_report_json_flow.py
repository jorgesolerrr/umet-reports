import json
from src.extract_data_flow import process_data
from src.utils.redis_client import RedisClient
from src.build_report_json import build_course_report

from src.utils.logging.logger_factory import get_logger

logger = get_logger()

def main_build_report(periods: list[str], ofg_pos: int):
    redis_client = RedisClient()
    for period in periods:
        build_report_json_flow_init(redis_client, period, ofg_pos)

def build_report_json_flow_init(redis_client: RedisClient, period: str, ofg_pos: int):
    logger.info(f"Building report json for period {period}")
    all_courses = redis_client.get_hset_keys_with_prefix(f"{period}:")
    logger.info(f"Found {len(all_courses)} courses for period {period}")
    redis_client.client.rpush("total_report_json", json.dumps([]))
    redis_client.client.rpush("module_indexes", json.dumps({}))
    
    process_data(all_courses, 10, build_report_json_flow, redis_client, period, ofg_pos)
    


def build_report_json_flow(chunk: list[str], redis_client: RedisClient, period: str, ofg_pos: int):
    processed_courses = 0
    for course_key in chunk:
        try:
            logger.info(f"Building report json for course {course_key}")
            course_info = redis_client.get_hset(course_key)
            course_name = course_key.split(":")[1]
            course_data, module_indexes = build_course_report(course_info, course_name, ofg_pos)
            redis_client.client.rpush("total_report_json", json.dumps(course_data))
            redis_client.client.rpush("module_indexes", json.dumps(module_indexes))
            logger.info(f"Report json for course {course_key} built")
            processed_courses += 1
        except Exception as e:
            logger.error(f"Error building report json for course {course_key}: {e}")
            continue
    return processed_courses       
