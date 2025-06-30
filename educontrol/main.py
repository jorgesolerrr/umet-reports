#!/usr/bin/env python3
"""
Proyecto EduControl
"""

from src.utils.logging.logger_factory import setup_logging
from src.extract_data_flow import extract_courses_data_flow
from src.utils.db import get_db, get_available_api_lms
from src.build_report_json_flow import main_build_report
from src.build_report import MakeQuantitativeReport
from src.utils.redis_client import RedisClient

def main():
    setup_logging()
    db = next(get_db())
    # available_api_lms = get_available_api_lms(db)
    # for api_lms in available_api_lms:
    #     #extract_courses_data_flow(api_lms, max_workers=8)
    #     #main_build_report(api_lms.periods, -3)
    MakeQuantitativeReport(RedisClient())


if __name__ == "__main__":
    main()
