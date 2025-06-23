"""
Proyecto EduControl
"""

from src.utils.logging.logger_factory import setup_logging
from src.extract_data_flow import extract_courses_data_flow
from src.utils.db import get_db, get_available_api_lms
from src.build_report_json_flow import main_build_report
from src.build_report import MakeQuantitativeReport, make_report
from src.utils.redis_client import RedisClient
from src.utils.category_finder import GradeCategoryBuilder, PostCategoryBuilder
import pandas as pd


test_params = {
    "ofg_pos": -3,
    "resources-cort-1": 30,
    "resources-cort-2": 40,
    "resources-cort-3": 50,
    "resources-cort-4": 50,
    "activity-cort-1": 5,
    "activity-cort-2": 10,
    "activity-cort-3": 15,
    "activity-cort-4": 16,
}

test_post = {
    "ofg_pos": -5,
    "resources-cort-1": 60,
    "activity-cort-1": 3,
}

test_prof = {
    "ofg_pos": -5,
    "resources-cort-1": 45,
    "activity-cort-1": 1,
}

CATEGORY_BUILDER = {
    "CESDEL-CARRERAS(NEW)": GradeCategoryBuilder,
    "CESDEL-POST(NEW)": PostCategoryBuilder,
}

def main():
    setup_logging()
    db = next(get_db())
    redis_client = RedisClient()
    available_api_lms = get_available_api_lms(db)
    for api_lms in available_api_lms:
        ofg_pos = api_lms.report_params["ofg_pos"]
        extract_courses_data_flow(api_lms, max_workers=8)
        main_build_report(api_lms.periods, ofg_pos)
        excel_rep = MakeQuantitativeReport(
            redis_client,
            CATEGORY_BUILDER[api_lms.lmsName](),
            api_lms.report_params,
            api_lms.current_cort,
        )
        make_report(excel_rep["excel"], filename=f"reporte_{api_lms.lmsName}_{pd.Timestamp.now().strftime('%Y%m%d')}-{api_lms.current_cort}.xlsx")
        redis_client.client.flushall()


if __name__ == "__main__":
    main()
